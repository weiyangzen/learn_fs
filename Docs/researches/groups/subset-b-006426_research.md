# Research: subset-b-006426

Grouped research for the CS35L3x/CS35L41 codec transport files under `sources/distributed-fs/ceph-client/sound/soc/codecs`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.c

## Purpose

`cs35l33.c` is the ALSA SoC codec and I2C driver for the Cirrus Logic CS35L33 smart amplifier. It binds an I2C device, validates the chip ID, applies a small register patch, exposes a single ASoC DAI with playback and capture, and manages power, clocks, DAPM routing, interrupt handling, and runtime PM for the amplifier, boost converter, and monitor ADC paths.

## Important APIs, Types, And Functions

The central state object is `struct cs35l33_private`, which stores the component pointer, platform data from `struct cs35l33_pdata`, the `regmap`, optional reset GPIO, runtime calibration state, internal MCLK, regulator bulk handles for `VA` and `VP`, and mode flags for TDM and soft ramp. Register access is constrained by `cs35l33_volatile_register`, `cs35l33_writeable_register`, and `cs35l33_readable_register`, with an 8-bit register and value `regmap_config` using `REGCACHE_MAPLE`.

The ASoC surface is `soc_component_dev_cs35l33` and `cs35l33_dai`. Key DAI operations are `cs35l33_pcm_startup`, `cs35l33_set_tristate`, `cs35l33_set_dai_fmt`, `cs35l33_pcm_hw_params`, and `cs35l33_set_tdm_slot`. Component-level sysclk selection is implemented by `cs35l33_component_set_sysclk`, not as a DAI sysclk op. DAPM events are handled by `cs35l33_spkrdrv_event`, `cs35l33_sdin_event`, and `cs35l33_sdout_event`. Device binding and teardown are `cs35l33_i2c_probe` and `cs35l33_i2c_remove`.

## Control Flow

Probe allocates state, creates an I2C regmap, puts the cache in cache-only mode, obtains `VA`/`VP` regulators, parses platform data or device-tree properties, requests the optional IRQ and reset GPIO, enables supplies, releases reset, waits for boot, enables the regmap, reads and validates the device ID with `cirrus_read_device_id`, reads the revision, applies `cs35l33_patch`, disables MCLK/TDM output, enables runtime PM autosuspend, and registers the ASoC component/DAI.

On component probe, the driver takes a runtime PM reference, disables the alive watchdog paths, programs boost, amplifier driver selection, optional boost peak current, optional digital soft ramp, IMON scaling, and hybrid-gain settings, unmasks critical interrupts, and drops the runtime PM reference. PCM startup constrains rates to the supported source-rate table. `hw_params` maps internal MCLK plus sample rate to an ADSP rate and internal-FS bit; in TDM mode it also programs the audio RX depth from sample width. TDM slot configuration interprets RX and TX masks, maps monitor streams to slot locations, toggles VPMON/VBSTMON DAPM routes, and enables TX slot registers.

DAPM controls sequencing around the amplifier. `SDIN` powers the boost and optionally starts one-time amp calibration; `SPKDRV` completes calibration after a delay and clears `CS35L33_AMP_CAL`; `SDOUT` switches tristate and TDM power bits based on whether TDM mode was selected. Bias prepare powers the chip and enables MCLK; standby powers down and may disable MCLK after `PDN_DONE`.

## State And Persistence Behavior

Most hardware state is held in regmap cache and restored through runtime PM. Runtime suspend marks the cache dirty, disables supplies, and resets `amp_cal` so calibration is redone after the next power-up. Runtime resume enables supplies, disables cache-only mode, releases reset, waits `CS35L33_BOOT_DELAY`, and syncs the cache. Persistent software state includes parsed platform data, the selected internal MCLK, `is_tdm_mode`, `enable_soft_ramp`, and `amp_cal`.

## Dependencies And Integration Points

The driver depends on Linux I2C, regmap, regulators, GPIO descriptors, runtime PM, ASoC component/DAI/DAPM APIs, and `cirrus_legacy.h` for device ID reading. It consumes public platform data from `include/sound/cs35l33.h` and local register definitions from `cs35l33.h`. Device-tree integration uses `cirrus,cs35l33` plus properties such as `cirrus,boost-ctl`, `cirrus,ramp-rate`, `cirrus,boost-ipk`, `cirrus,imon-adc-scale`, and child node `cirrus,hg-algo`.

## Risks And Edge Cases

Clocking is strict: unsupported MCLK/sample-rate pairs cause `hw_params` failure. `set_tdm_slot` only accepts 8-bit slots and assumes a fixed order for monitor stream assignment. IRQ registration failure is only warned, so systems can operate without interrupt-driven fault reporting. Several regmap updates ignore return values, so some I2C failures may not abort configuration. The reset GPIO is optional, but resume unconditionally toggles it; this relies on gpiod helpers accepting NULL. Calibration state is software-only and can become stale if power sequencing happens outside runtime PM. Device-tree HG and boost values are lightly range-checked compared with their field widths.

## Test Signals

Useful validation signals are successful probe messages with the expected chip ID/revision, ASoC card registration with one playback and one capture stream, `hw_params` acceptance for supported MCLK/rate combinations, DAPM power sequencing that toggles boost and MCLK as expected, TDM slot register updates for RX/TX masks, runtime suspend/resume regcache sync without errors, and interrupt logs for amp short, calibration, overtemperature, clock, and monitor overflow faults. No tests were run for this research pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.h

## Purpose

`cs35l33.h` is the local register and bit-field definition header used by `cs35l33.c`. It describes the CS35L33 register map, supported clock constants, ASoC PCM rate/format masks, power-control bits, serial-port routing fields, interrupt bits, boost-control fields, and hybrid-gain/class-H algorithm controls.

## Important APIs, Types, And Constants

The header does not define functions or private structs. Its exported surface is a dense set of preprocessor constants. The most important groups are the chip/register identifiers (`CS35L33_CHIP_ID`, `CS35L33_DEVID_*`, `CS35L33_PWRCTL*`, `CS35L33_CLK_CTL`, `CS35L33_TX_*`, `CS35L33_RX_*`), supported MCLK values, `CS35L33_RATES`, `CS35L33_FORMATS`, power-down masks for amplifier, boost, monitor ADCs, TDM, SDIN, and SDOUT tristate, interrupt mask/status bits, protection-release bits, and field masks/shifts for boost, DAC soft ramp, class-D gain, monitor slot locations, and HG/class-H behavior.

## Control Flow

There is no executable control flow in the header, but it drives the control flow in `cs35l33.c`. The DAPM handlers use `CS35L33_PDN_*` and tristate bits to sequence boost, serial input, and serial output. The clock setup path uses `CS35L33_MCLK_*`, `CS35L33_MCLKDIV2`, `CS35L33_ADSP_FS`, and `CS35L33_INT_FS_RATE` to translate external MCLK to internal sampling configuration. The TDM setup path relies on `CS35L33_X_STATE`, `CS35L33_X_LOC`, and `CS35L33_AUDIN_RX_DEPTH` to configure monitor and audio slots. Fault handling uses `CS35L33_INT_STATUS_*`, interrupt mask bits, and release bits in `CS35L33_AMP_CTL`.

## State And Persistence Behavior

The header defines how state is encoded in hardware registers. Persistent state is not stored here, but the constants determine which registers are cached by regmap and which are considered volatile or read-only in the C file. The definitions also establish defaults that must remain consistent with the hardware datasheet and the `cs35l33_reg` table.

## Dependencies And Integration Points

This local header depends on ALSA PCM format/rate macros being visible through the including C file. It integrates with the public platform-data header `include/sound/cs35l33.h` indirectly: platform values are shifted and masked with definitions from this file before being written to hardware. It is tightly coupled to the CS35L33 datasheet and to `cs35l33.c`'s regmap readability, DAPM, DAI, and IRQ code.

## Risks And Edge Cases

The primary risk is register-definition drift: incorrect masks, shifts, or constants can silently program unsafe boost, power, or protection values. Some masks represent active-low power-down semantics, which is easy to misuse. The header contains non-obvious monitor-routing encodings where a state bit and location field share a register. `CS35L33_FORMATS` only includes 16- and 24-bit little-endian PCM, while the TDM slot code assumes 8-bit slots and derives sample depth separately.

## Test Signals

Compile coverage is the first signal: all macros must resolve in `cs35l33.c`. Runtime signals include correct probe ID matching, valid regmap readable/writeable behavior, successful supported-rate `hw_params`, correct DAPM power transitions, and expected IRQ decoding for each status bit. No standalone tests were run for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l33.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.c

## Purpose

`cs35l34.c` is the ALSA SoC codec and I2C driver for the Cirrus Logic CS35L34 amplifier. It initializes the I2C device, validates identity, configures regulators/reset/IRQ, registers an ASoC component and DAI, manages DAPM power sequencing, maps clocks and TDM slots, applies platform boost and amplifier options, and handles critical fault interrupts.

## Important APIs, Types, And Functions

`struct cs35l34_private` holds the component pointer, `struct cs35l34_platform_data`, regmap, `VA`/`VP` supplies, internal MCLK, TDM mode flag, and reset GPIO. Register behavior is described by `cs35l34_volatile_register`, `cs35l34_readable_register`, and `cs35l34_precious_register`; status registers are precious because reads acknowledge interrupt state. `cs35l34_sdin_event`, `cs35l34_main_amp_event`, and `cs35l34_mclk_event` implement DAPM sequencing. `cs35l34_set_tdm_slot`, `cs35l34_set_dai_fmt`, `cs35l34_pcm_hw_params`, `cs35l34_set_tristate`, and `cs35l34_dai_set_sysclk` implement DAI behavior. `cs35l34_probe` is the component probe, while `cs35l34_i2c_probe`, `cs35l34_i2c_remove`, runtime PM callbacks, and module init/exit implement bus-driver lifecycle.

## Control Flow

I2C probe allocates state, initializes the 8-bit regmap, gets and enables `VA`/`VP`, parses platform data or device tree, requests an IRQ, obtains reset GPIO, releases reset, waits for startup, reads and validates the chip ID/revision, unmasks critical interrupts, enables runtime PM, and registers the component. Component probe then programs power-control defaults, mutes the amplifier, applies platform boost peak, gain zero-cross, ADSP drive, digital soft-ramp, inversion, boost inductor, I2S input location, and TDM edge settings.

During playback startup, the DAPM `SDIN` event powers the device and, in TDM mode, clears `PDN_TDM`. `Main AMP` sets the boost voltage, waits, and unmutes on power-up; on power-down it clears boost voltage and mutes. `EXTCLK` power-down waits either for soft-ramp settling or a shorter delay, then polls `CS35L34_INT_STATUS_2` up to `PDN_DONE_ATTEMPTS` for `PDN_DONE`. DAI sysclk accepts 5.6448, 6, 6.144, 11.2896, 12, and 12.288 MHz, with high rates divided by two before using the MCLK/rate table. `hw_params` writes the ADSP sample-rate code. TDM setup only supports 8-bit slots and maps RX audio plus monitor TX streams into TDM slot enable registers.

## State And Persistence Behavior

Runtime PM suspends by enabling regcache cache-only mode, marking the cache dirty, asserting reset, and disabling supplies. Runtime resume reenables supplies, reenables live regmap access, releases reset, waits, and syncs cached registers. The component keeps `mclk_int` and `tdm_mode` as software state. Platform data persists for boost voltage, boost current, inductor, drive strength, ramping, inversion, and routing options.

## Dependencies And Integration Points

The driver integrates with Linux I2C, regmap, regulator, GPIO, runtime PM, OF, IRQ, and ASoC APIs. It uses `cirrus_read_device_id` from `cirrus_legacy.h`, local register definitions in `cs35l34.h`, and public platform data from `include/sound/cs35l34.h`. Device-tree binding uses `cirrus,cs35l34` and properties including `cirrus,boost-vtge-millivolt`, `cirrus,boost-ind-nanohenry`, `cirrus,boost-peak-milliamp`, `cirrus,aif-half-drv`, `cirrus,digsft-disable`, `cirrus,gain-zc-disable`, `cirrus,amp-inv`, `cirrus,i2s-sdinloc`, and `cirrus,tdm-rising-edge`.

## Risks And Edge Cases

`cirrus,boost-ind-nanohenry` is required in OF mode; missing it fails probe. IRQ request failure logs an error but does not abort, weakening hardware-fault handling. Several register writes ignore return values. TDM slot numbering has hard-coded monitor ordering and 8-bit-only slot width. The `cs35l34_sdin_event` stores `ret` on POST_PMD but returns 0, masking a failure. `cs35l34_mclk_event` logs but does not fail when PDN_DONE times out. Runtime PM is enabled only after initial configuration, and probe error paths must keep reset/regulators balanced.

## Test Signals

Validation should cover probe success, device ID mismatch failure, mandatory OF property failure, supported and unsupported sysclk/rate pairs, TDM slot programming, DAPM mute/boost transitions, runtime PM cache sync after suspend/resume, and IRQ handling for calibration, alive, amp short, overtemperature, boost-high, and inductor-short faults. No tests were run for this research pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.h

## Purpose

`cs35l34.h` provides the local CS35L34 register map, clock values, PCM capability masks, interrupt definitions, power-control masks, boost/class-H/brownout/TDM register fields, and protection-release bits used by `cs35l34.c`.

## Important APIs, Types, And Constants

The header has no functions or data structures. It defines `CS35L34_CHIP_ID`, all relevant 8-bit register addresses through `CS35L34_OTP_TRIM_STATUS`, `CS35L34_MAX_REGISTER`, and `CS35L34_REGISTER_COUNT`. Important field groups include `CS35L34_PWRCTL*` power bits, `CS35L34_ADSP_CLK_CTL` and `CS35L34_MCLK_CTL` clock fields, amplifier digital volume/protection bits, boost voltage and peak-current masks, TDM RX/TX location and enable registers, critical interrupt mask/status bits across four interrupt banks, and `CS35L34_RATES`/`CS35L34_FORMATS`.

## Control Flow

The C file uses these constants to drive probe defaults, component probe platform-data programming, DAI sysclk and sample-rate setup, TDM slot routing, DAPM power transitions, and interrupt release cycles. The `CS35L34_X_STATE` and `CS35L34_X_LOC` fields are central to monitor slot routing. `CS35L34_PDN_DONE` is polled during DAPM MCLK power-down. Critical masks select which hardware faults are unmasked during probe.

## State And Persistence Behavior

This header encodes hardware state but stores no runtime state. Its register definitions must align with the regmap default table and readable/volatile/precious callbacks in `cs35l34.c`. Status registers are read-to-ack in the driver, so the constants for interrupt banks and bits are persistence-critical for correct fault recovery.

## Dependencies And Integration Points

The header relies on ALSA PCM macros from the including context for `CS35L34_RATES` and `CS35L34_FORMATS`. It is paired with public platform data from `include/sound/cs35l34.h`, whose fields are translated into the masks and shifts defined here. It is not a standalone API for other drivers.

## Risks And Edge Cases

Incorrect masks or shifts can cause unsafe boost voltage/current, wrong monitor routing, failed power-down detection, or missed critical interrupts. The header contains both mask and status definitions with similar names; confusion between `M_*` mask bits and status bits would produce inverted behavior. Some fields define active-low power-down semantics and require careful use in DAPM code.

## Test Signals

Compile success of `cs35l34.c` is the basic signal. Runtime validation should include known-good register writes for boost, MCLK, ADSP rate, TDM TX/RX slot routing, PDN_DONE polling, and IRQ decode/release for each status bank. No standalone tests were run for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l34.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.c

## Purpose

`cs35l35.c` is the ALSA SoC codec/I2C driver for the Cirrus Logic CS35L35 amplifier. It supports PCM and PDM DAIs, configures boost/class-H/monitor paths from platform data or device tree, applies a revision-A0 errata patch, manages shared-reset and regulator startup, exposes audio and advisory controls, and handles protection interrupts including a `PDN_DONE` completion used during DAPM shutdown.

## Important APIs, Types, And Functions

The private state lives in `struct cs35l35_private`, defined in `cs35l35.h`, and includes device, platform data, regmap, regulators, sysclk/SCLK values, PDM/I2S flags, clock-provider role, reset GPIO, and `struct completion pdn_done`. Register callbacks are `cs35l35_volatile_register`, `cs35l35_readable_register`, and `cs35l35_precious_register`. DAPM sequencing is handled by `cs35l35_sdin_event`, `cs35l35_main_amp_event`, and helper `cs35l35_wait_for_pdn`. DAI behavior is split between PCM ops (`cs35l35_pcm_startup`, `cs35l35_set_dai_fmt`, `cs35l35_hw_params`, `cs35l35_dai_set_sysclk`) and PDM ops (`cs35l35_pdm_startup`, common format and params). Component sysclk is `cs35l35_component_set_sysclk`.

## Control Flow

I2C probe allocates state, initializes regmap, obtains regulators, parses platform data or OF, enables supplies, gets optional reset GPIO, performs reset, initializes the completion, requests a shared threaded IRQ, validates chip ID/revision, applies `cs35l35_errata_patch`, programs critical interrupt masks, powers down blocks, mutes the amplifier, and registers two DAIs. Component probe applies platform configuration: boost voltage/current/inductor, gain zero-cross, audio/advisory channel selection, stereo/shared-boost mode, serial-port drive strength, class-H algorithm fields, and optional monitor-signal routing/depth/scaling.

For PCM startup, the driver constrains rates to 44.1 through 192 kHz and clears PDM mode. PDM startup constrains rates to 44.1 through 96 kHz and sets PDM mode. `set_fmt` selects clock provider/consumer and I2S versus PDM. `component_set_sysclk` selects MCLK, SCLK, or PDM clock and records the supported sysclk frequency. `hw_params` maps sysclk plus sample rate to a clock control value, applies an A0 class-H weak-FET erratum when needed, programs audio input depth for playback, and validates SCLK/FS ratios for I2S based on clock role.

DAPM `SDIN` power-up enables MCLK and clears global power-down; power-down asserts discharge/global power-down, disables volume ramp for faster shutdown, waits for `PDN_DONE` unless an external boost is configured, disables MCLK, and restores digital soft ramp. `Main AMP` controls boost FET state, mute, PDM boost-voltage switching, and status draining.

## State And Persistence Behavior

The driver has no runtime PM callbacks; regulators remain enabled for the lifetime of the bound device until remove or probe error. Regmap cache still records defaults and readable/volatile/precious behavior. Persistent software state includes parsed platform data, sysclk/SCLK, mode flags, clock-consumer role, and completion state. The `CS35L35_VALID_PDATA` flag is used while parsing properties where zero is valid; the component probe tests nonzero values before writing, so flagged values include the high marker bit and rely on masks to discard it during `regmap_update_bits`.

## Dependencies And Integration Points

The driver depends on Linux I2C, regmap, regulators, GPIO descriptors, OF, completions, IRQ, ASoC component/DAI/DAPM/control APIs, and `cirrus_read_device_id`. It uses public data structures from `include/sound/cs35l35.h` and local register definitions in `cs35l35.h`. Device-tree properties include boost settings, reset sharing, stereo/shared-boost flags, class-H child configuration, and `cirrus,monitor-signal-format` arrays for IMON/VMON/VPMON/VBSTMON/VPBR status/zerofill routing.

## Risks And Edge Cases

The high-bit valid marker pattern is fragile: if a field is written without an appropriate mask, the marker can leak into hardware values. Some class-H parsing duplicates `cirrus,classh-bst-max-limit` and appears to read `cirrus,classh-bst-overide` from the parent node rather than the child node. In monitor configuration, the VBSTMON depth write uses `monitor_config->vpmon_dpth`, which may be intentional or a copy/paste bug. `cs35l35_wait_for_pdn` depends on IRQ delivery; if IRQ registration fails, probe fails, but missed PDN interrupts can still cause shutdown timeout. Shared reset is tolerated on `-EBUSY`, but reset sequencing with multiple amplifiers must be validated at board level.

## Test Signals

Key signals are successful probe and A0 patch application, component registration with `cs35l35-pcm` and `cs35l35-pdm`, expected sysclk/rate acceptance and rejection, correct SCLK/FS ratio validation for clock provider and consumer modes, DAPM shutdown completion via `PDN_DONE`, stereo advisory controls appearing only when configured, monitor TX routing writes matching device tree, and IRQ logs/release writes for calibration, amp-short, overtemperature, boost, VPBR, and monitor overflow faults. No tests were run for this research pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.h

## Purpose

`cs35l35.h` is the local register, bit-field, and private-state header for the CS35L35 codec driver. Unlike the CS35L33/34 local headers, it also defines `struct cs35l35_private` and the static supply-name table used by `cs35l35.c`.

## Important APIs, Types, And Constants

The header defines the register range (`CS35L35_FIRSTREG`, `CS35L35_LASTREG`, `CS35L35_MAX_REGISTER`), chip ID, all 8-bit register addresses, power-down bits, serial-port format fields, clock-source fields, RX/TX depth and location fields, boost converter coefficients, class-H controls, protection release bits, interrupt status masks, and PCM format support. `struct cs35l35_private` stores device, public platform data, regmap, supplies, sysclk/SCLK, PDM/I2S mode flags, clock-consumer flag, reset GPIO, and `pdn_done` completion.

## Control Flow

The constants are consumed throughout probe, component probe, DAI setup, DAPM events, and IRQ handling. Clock and serial-format masks control `set_fmt`, `set_sysclk`, and `hw_params`. Power bits drive DAPM transitions for global power-down, boost FET behavior, MCLK disable, and monitor blocks. Interrupt masks and status values control both critical-error unmasking in probe and release cycles in `cs35l35_irq`.

## State And Persistence Behavior

The header itself has no persistence, but it defines the private structure that carries all runtime state. It also defines static `cs35l35_supplies[] = { "VA", "VP" }`, which the I2C probe copies into regulator bulk descriptors. The register macros define what is cacheable or volatile in `cs35l35.c`.

## Dependencies And Integration Points

This file depends on public platform data from `include/sound/cs35l35.h`, Linux regmap/regulator/GPIO/completion types through the including C file, and ALSA PCM macros for `CS35L35_FORMATS`. It is coupled directly to the implementation file and should not be treated as a broad subsystem header.

## Risks And Edge Cases

Because it mixes register definitions, private driver state, and a static supply array, changes here can affect both hardware programming and object layout. Incorrect depth/location masks can break capture stream layout. The interrupt mask constants (`CS35L35_INT*_CRIT_MASK`) encode the default safety posture; wrong values can hide or over-report critical faults. The header defines only formats, while rates are constrained dynamically in C.

## Test Signals

Compile success, correct private-struct initialization in probe, successful regulator lookup for `VA` and `VP`, valid regmap readable/volatile handling, expected DAI format negotiation, and correct IRQ bit decoding are the main validation signals. No standalone tests were run for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.c

## Purpose

`cs35l36.c` is the ALSA SoC codec/I2C driver for CS35L36/CS35L37-family Cirrus Logic amplifiers. It uses 32-bit register addressing, configures the PLL and ASP audio interface, supports monitor capture muxes, applies revision-specific errata and PAC firmware trim flows, parses board-specific boost/VPBR/IRQ parameters, clamps unsafe 10V device settings, and handles critical protection interrupts.

## Important APIs, Types, And Functions

`struct cs35l36_private` stores device, public platform data, regmap, `VA`/`VP` supplies, selected PLL source, chip version, revision ID, low-power/PDM LDM state, and reset GPIO. Clock tables are `cs35l36_pll_sysclk` and `cs35l36_fs_rates`. Register callbacks are `cs35l36_readable_reg`, `cs35l36_precious_reg`, and `cs35l36_volatile_reg`. Controls include digital/analog volume, PCM soft ramp, gain zero-cross, PDM LDM ramp switches, and `LDM Select Switch`, with custom get/put handlers updating `CS35L36_NG_CFG`.

DAPM and routing are defined by `cs35l36_dapm_widgets` and `cs35l36_audio_map`, including channel muxing, boost/class-H/main-amp sequencing, six ASP TX capture paths, and monitor-source muxes. DAI operations are `cs35l36_set_dai_fmt`, `cs35l36_pcm_hw_params`, and `cs35l36_dai_set_sysclk`. Component sysclk/PLL setup is `cs35l36_component_set_sysclk`. Probe helpers include `cs35l36_handle_of_data`, `cs35l36_pac`, `cs35l36_apply_vpbr_config`, `cs35l36_boost_inductor`, and `cs35l36_component_probe`.

## Control Flow

I2C probe initializes the 32-bit regmap, obtains regulators, parses platform data or required OF properties, enables supplies, gets optional reset GPIO, releases reset, validates `CS35L36_SW_RESET` against `CS35L36_CHIP_ID`, reads revision and OTP chip-version data, applies A0 or B0 errata, runs the B0 PAC sequence when required, applies VPBR configuration, derives IRQ polarity from the parent IRQ descriptor, programs chip IRQ polarity/output, requests the threaded IRQ, unmasks critical interrupts, logs CS35L36 versus CS35L37 identity, and registers the component/DAI.

Component probe applies revision/board configuration: A0 DCM mode workarounds, PCM inversion, multi-amp TX Hi-Z, IMON/VMON polarity, boost voltage/control/current/inductor, temperature threshold, IRQ drive/GPIO selection, 10V L36 safety clamping, and disabling `SYNC_GLOBAL_OVR` when global enable is low. `set_fmt` configures ASP provider/consumer clocking, continuous/gated clocks, I2S versus DSP_A, and clock inversion bits. `hw_params` maps sample rate to global FS and programs RX or TX ASP frame width. DAI sysclk updates test-key-protected FS monitor windows. Component sysclk selects PLL reference source/frequency, toggles open-loop/reference-enable bits, applies A0 PLL tuning, and switches PDM mode with noise-gate delay handling when entering or leaving PDM clock source.

DAPM power-up of `Main AMP` asserts global enable, checks PLL unlock, selects PCM input, and unmutes. Power-down selects zero input, mutes, and clears global enable. `BOOST Enable` toggles boost state unless an external boost is configured.

## State And Persistence Behavior

There is no runtime PM implementation in this file; regulators stay enabled while bound and are disabled in remove/error paths. Regmap caches a large set of 32-bit defaults, with PAC program memory and interrupt/status areas marked volatile/readable as needed. Persistent software state includes revision, 10V/12V chip version, selected PLL clock source, LDM state, parsed platform data, and reset GPIO availability. Test-key unlock/lock sequences protect writes to sensitive hardware registers.

## Dependencies And Integration Points

The driver depends on Linux I2C, regmap, regulators, GPIO descriptors, IRQ trigger metadata, OF, ASoC component/DAI/DAPM/control APIs, and public platform data from `include/sound/cs35l36.h`. Local register definitions and the external `cs35l36_a0_pac_patch` declaration live in `cs35l36.h`; the C file itself programs B0 PAC memory with `CS35L36_B0_PAC_PATCH`. Device-tree requires boost voltage, boost peak current, and boost inductor, and may provide multi-amp, DCM, inversion, polarity, IRQ, temperature, boost-select, and `cirrus,vpbr-config` child properties.

## Risks And Edge Cases

OF mode fails probe if required boost parameters are missing or out of range. The `CS35L36_VALID_PDATA` marker is ORed into several fields; writes must always be masked to avoid leaking the marker bit. `hw_params` silently leaves global FS unchanged for unsupported rates in the table, then may still return success if the format width is valid. `cs35l36_irq` appears to use `CS35L36_TEMP_ERR_RLS` for the boost over-voltage release path, which is worth verifying against the datasheet. The PAC loop returns `-EINVAL` after polling rather than a timeout-specific code. There is no runtime PM, so idle power depends entirely on DAPM and board-level expectations.

## Test Signals

Validation should cover A0 and B0 probe paths, PAC completion, 10V versus 12V OTP detection and clamping, required OF property failures, IRQ polarity programming for low/high/falling/rising triggers, supported PLL reference frequencies, ASP format and inversion negotiation, global FS and frame-width writes for playback/capture, PDM clock-source switching with LDM enabled, DAPM PLL-unlock warning behavior, and critical IRQ release cycles for amp short, temperature, boost OVP/UVP, and inductor-short errors. No tests were run for this research pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.h

## Purpose

`cs35l36.h` is the local register and bit-field header for the CS35L36/CS35L37 ASoC codec driver. It defines the large 32-bit register map, interrupt masks, PLL/ASP/PDM/boost/VPBR fields, revision and OTP identifiers, protected test-key values, PAC memory constants, supported PCM formats, and an external PAC patch symbol.

## Important APIs, Types, And Constants

The header includes `<linux/regmap.h>` and defines register addresses from reset and OTP through PAC program memory. Important groups include ASP clock/provider/inversion/format fields, ASP RX/TX width and slot fields, PLL reference selection and frequency encoding fields, PCM input selection, global enable and global FS masks, power-up/down status bits, FS monitor windows, boost converter controls, class-H/noise-gate/PDM fields, interrupt defaults and reset masks, critical error bits and release bits, revision IDs (`A0`, `B0`), OTP L37 detection, VPBR configuration masks, test-key unlock/lock values, and `CS35L36_RX_FORMATS`/`CS35L36_TX_FORMATS`. It declares `extern const int cs35l36_a0_pac_patch[CS35L36_PAC_PROG_MEM];`.

## Control Flow

These constants drive every major path in `cs35l36.c`: regmap readability/volatility, revision-specific patching, PAC memory programming, device ID and OTP chip-version detection, PLL setup, ASP DAI format and `hw_params`, DAPM amp/boost sequencing, VPBR application, 10V safety clamping, IRQ release cycles, and remove-time interrupt mask reset.

## State And Persistence Behavior

No mutable state is stored in this header. It defines register encodings that the C file caches through `REGCACHE_MAPLE`, marks as volatile, or writes through test-key-protected sequences. Constants such as default interrupt masks and PAC memory sizes are persistence-relevant because they shape boot-time hardware state and remove-time cleanup.

## Dependencies And Integration Points

The header is local to the codec implementation and public platform data in `include/sound/cs35l36.h`. It depends on ALSA PCM macros from the inclusion context and on regmap type availability. It also declares a PAC patch array that must be provided by another compilation unit or build configuration for successful linkage if referenced.

## Risks And Edge Cases

The register space is broad and sparse; an incorrect address or stride assumption can break regmap access. Some macros have names beginning `CS35L35_` while being used in CS35L36 boost-control writes, which is confusing even if numerically intentional. Default interrupt masks encode safety behavior and should be reviewed carefully when changing fault handling. Test-key constants protect sensitive registers; missing lock writes can leave test mode open.

## Test Signals

Compile/link success, regmap access to 32-bit stride registers, successful A0/B0 patch application, correct PLL/ASP field updates, IRQ default/reset mask writes, and probe-time chip-version detection are the main validation signals. No standalone tests were run for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-i2c.c

## Purpose

`cs35l41-i2c.c` is the I2C transport wrapper for the CS35L41 codec family driver. It does not implement the codec logic itself; it allocates and initializes `struct cs35l41_private`, creates an I2C regmap using `cs35l41_regmap_i2c`, wires IRQ/device/platform-data fields, and delegates probe/remove and PM behavior to the shared CS35L41 core.

## Important APIs, Types, And Functions

The main functions are `cs35l41_i2c_probe` and `cs35l41_i2c_remove`. The file exports match tables for I2C IDs (`cs35l40`, `cs35l41`, `cs35l51`, `cs35l53`), OF compatibles (`cirrus,cs35l40`, `cirrus,cs35l41`), and ACPI ID `CSC3541`. `cs35l41_i2c_driver` binds those tables to Linux I2C and references `pm_ptr(&cs35l41_pm_ops)` from the shared core. The module is registered with `module_i2c_driver`.

## Control Flow

On probe, the driver obtains optional platform hardware configuration with `dev_get_platdata`, allocates `struct cs35l41_private` with devm lifetime, records `dev` and `client->irq`, stores the private pointer with `i2c_set_clientdata`, creates the regmap via `devm_regmap_init_i2c`, and returns `cs35l41_probe(cs35l41, hw_cfg)`. Regmap allocation failures are reported with `dev_err_probe`. Remove fetches the private data with `i2c_get_clientdata` and calls `cs35l41_remove`.

## State And Persistence Behavior

This file owns only transport-level state setup. All persistent codec state, supplies, reset GPIO, DSP state, firmware, controls, IRQ handling, and runtime/system PM behavior live in the shared CS35L41 implementation. Device-managed allocation means the wrapper has minimal explicit cleanup beyond delegating remove.

## Dependencies And Integration Points

The wrapper depends on Linux I2C, ACPI, OF, module, platform-data, slab allocation, and regmap through the shared header. It includes `cs35l41.h`, which defines `struct cs35l41_private`, `cs35l41_probe`, `cs35l41_remove`, `cs35l41_pm_ops`, and the core hardware config type. It integrates with `cs35l41-lib.c` for `cs35l41_regmap_i2c` and `cs35l41.c` for core probe/remove/PM.

## Risks And Edge Cases

The I2C ID table includes multiple related part names while OF only lists CS35L40 and CS35L41; support for CS35L51/CS35L53 by name depends on the shared core correctly identifying and handling the part. If platform data is absent, the core must derive configuration from firmware/OF/ACPI. IRQ value is passed through without local validation. Because this wrapper is intentionally thin, most behavioral risks are in the shared core, but transport regmap mismatch would prevent all later setup.

## Test Signals

Useful signals are I2C modalias/OF/ACPI matching, successful regmap allocation, entry into shared `cs35l41_probe`, correct IRQ propagation, clean delegated remove, and PM callback use through the shared `cs35l41_pm_ops`. No tests were run for this research pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-i2c.c -->
