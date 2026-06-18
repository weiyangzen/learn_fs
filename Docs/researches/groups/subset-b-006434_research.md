# Group Research: subset-b-006434

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.c

## Purpose
`cs530x.c` is the common ASoC component implementation for the Cirrus CS530x/CS430x family: 2-channel codec, DAC-only, and ADC-only variants up to 8 channels. It does not bind to a bus directly; instead it exports I2C and SPI `regmap_config` objects plus `cs530x_probe()` for bus wrapper drivers. The file owns codec registration, DAI setup, DAPM topology construction, power/reset sequencing, channel-count discovery, and audio clock/format programming.

## Important APIs, Types, and Functions
The public surface is `cs530x_probe(struct cs530x_priv *cs530x)` and the exported namespace symbols `cs530x_regmap_i2c` and `cs530x_regmap_spi`. Internally, `cs530x_readable_register()` and `cs530x_writeable_register()` define the regmap contract around ID, clock, ASP, input/output, volume, and pad registers. `cs530x_put_volsw_vu()` wraps normal ALSA volume writes and then writes `CS530X_INOUT_VU` so latched volume changes take effect. `cs530x_adc_event()` and `cs530x_dac_event()` manage mute/unmute sequencing for channel pairs during DAPM power transitions. `cs530x_hw_params()`, `cs530x_set_fmt()`, `cs530x_set_tdm_slot()`, `cs530x_set_sysclk()`, and `cs530x_set_pll()` implement the DAI/component clocking and format API. `cs530x_component_probe()` dynamically adds controls, widgets, and routes according to the exact detected device type.

## Control Flow
Probe duplicates the static DAI driver, obtains `vdd-a` and `vdd-io`, enables supplies, optionally toggles reset GPIO, reads and validates device ID/revision, optionally performs a software reset, parses high-impedance input properties, sets DAI capture/playback channel limits, and registers the component. Component probe then adds the shared global DAPM supply and variant-specific ADC/DAC widgets and controls. Runtime audio configuration enters through DAI ops: format selects codec/provider mode, I2S/left-justified/DSP_A framing, and BCLK inversion; hardware params maps sample rate to register codes and derives BCLK from PCM or TDM settings; TDM slot config maps accepted contiguous TX masks to the codec slot selector.

## State and Persistence
Persistent device state is held in regmap cache defaults and in `struct cs530x_priv`: bus regmap, device pointer, duplicated DAI, devtype, number of ADCs/DACs, supplies, reset GPIO, TDM width/slot count, and DAPM pair counters. Register cache type is `REGCACHE_MAPLE`. The DAPM event counters are transient synchronization state used to delay VU writes until all paired ADC/DAC widgets complete power-up. No filesystem or NVRAM state is used.

## Dependencies and Integration Points
The driver depends on Linux regmap, regulator, GPIO descriptor, device property, ALSA SoC component/DAI/DAPM, PCM params, and TLV control helpers. Bus wrappers must allocate/fill `struct cs530x_priv`, create a regmap with the exported config, set `devtype`, and call `cs530x_probe()`. Machine drivers interact through the `cs530x-dai` DAI and component-level `set_sysclk`/`set_pll`. Firmware properties include `cirrus,in-hiz-pin12`, `pin34`, `pin56`, and `pin78` depending on ADC count.

## Risks and Edge Cases
Supported rates and clocks are strict; unsupported BCLK, PLL refclk, MCLK, or sample-rate values return `-EINVAL`. `cs530x_set_tdm_slot()` only examines `tx_mask`, so capture-only wiring must still provide a compatible mask through the machine driver. TDM enable is checked from `CS530X_SIGNAL_PATH_CFG`, but `set_tdm_slot()` only writes the slot selector, so another path or reset default must set TDM enable for TDM BCLK math to be used. DAPM mute/unmute sequencing assumes widgets are powered in paired channel order and uses `w->shift` arithmetic to locate adjacent volume registers. Probe enables regulators manually and only disables them on probe failure; normal removal relies on devm lifetime and reset is not released by a remove callback in this common file.

## Test Signals
Useful checks include successful ID/revision read, channel max matching the silicon ID, visible ALSA controls only for the detected channel count, DAPM route creation for 2/4/8 channel ADC/DAC variants, rejection of unsupported sysclk/PLL/BCLK/sample rates, and VU-triggered volume changes taking effect. TDM tests should cover valid masks for 0-1 through 14-15, invalid sparse masks, and BCLK calculation with slot width/count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.h

## Purpose
`cs530x.h` is the private/shared header for CS530x-family bus drivers and the common component driver. It defines device IDs, register addresses, bit masks, supported clock constants, TDM slot encodings, the `enum cs530x_type`, the shared `struct cs530x_priv`, and the exported regmap/probe declarations.

## Important APIs, Types, and Constants
The key type is `struct cs530x_priv`, which carries the regmap, device, duplicated DAI driver, expected device type, detected ADC/DAC counts, regulator array, TDM settings, DAPM event counters, and optional reset GPIO. `enum cs530x_type` maps symbolic driver variants to actual hardware device IDs. Public declarations are `extern const struct regmap_config cs530x_regmap_i2c`, `extern const struct regmap_config cs530x_regmap_spi`, and `int cs530x_probe(struct cs530x_priv *cs530x)`.

## Register and Control Model
The register map is grouped into identity/reset, clock configuration, chip enable, ASP/signal path, ADC input controls, DAC output controls, and pad function/level registers. `CS530X_CLK_CFG_0` contains PLL ref source/frequency and sysclk source bits; `CS530X_CLK_CFG_1` stores sample-rate family; `CS530X_ASP_CFG` stores BCLK family, primary mode, and BCLK inversion; `CS530X_SIGNAL_PATH_CFG` stores ASP format, TDM slot selector, channel reverse, and TDM enable. Input/output volume registers use bit 15 as mute and the corresponding `*_VOL_CTRL5` register uses `CS530X_INOUT_VU` to latch updates.

## State and Persistence
The header defines no executable state, but it is the source of the persistent register contract used by regmap defaults and DAPM controls in the C file. The supply count is fixed at two. The clock constants constrain the runtime state accepted by the component APIs: direct MCLK sysclk accepts 45.1584 MHz and 49.152 MHz, while PLL/MCLK reference validation accepts 11.2896/12.288 MHz and 22.5792/24.576 MHz families in the implementation.

## Dependencies and Integration Points
The header includes Linux device, GPIO, regmap, and regulator consumer headers so bus-specific code can construct `cs530x_priv`. It is consumed by the common codec implementation and by bus glue modules in the same driver family. Machine drivers do not usually include this header directly; they use the registered ASoC DAI/component operations.

## Risks and Edge Cases
There are many near-identical masks and slot encodings, so maintenance errors are easy when adding variants or TDM layouts. The TDM mask constants encode groups rather than arbitrary channels, reflecting hardware limits. `CS530X_TDM_EN_MASK` is defined here, but the common `set_tdm_slot()` path only writes the slot selector; integrators need to ensure TDM enable is set by the intended configuration path. The SPI regmap uses 16-bit registers, 16-bit padding, 16-bit values, big-endian formatting, and stride 2, which must match the bus wrapper exactly.

## Test Signals
Compile coverage should catch exported declaration drift. Runtime tests should validate each `enum cs530x_type` against actual ID reads, confirm register maps are accepted over both I2C and SPI, and check that TDM masks in the header map to the expected `SIGNAL_PATH_CFG` values through `cs530x_set_tdm_slot()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.c

## Purpose
`cs53l30.c` is an ASoC I2C driver for the Cirrus CS53L30 four-channel ADC/DMIC codec. It registers one capture DAI, exposes controls for ADC routing/gain/noise gate/filtering, builds DAPM input and SDOUT routes, validates device identity, manages supplies/reset/mclk/mute GPIO, and implements runtime suspend/resume through regcache and regulators.

## Important APIs, Types, and Functions
`struct cs53l30_private` stores supplies, regmap, reset and mute GPIOs, optional `mclk`, `use_sdout2`, and the selected internal `mclk_rate`. Regmap callbacks mark interrupt status volatile, ID/revision/status registers read-only, and enumerate readable registers. Control tables expose digital soft ramp, noise gate, notch, invert, digital boost, preamp, PGA, and digital volume controls. DAI operations are `cs53l30_set_sysclk()`, `cs53l30_set_dai_fmt()`, `cs53l30_pcm_hw_params()`, `cs53l30_set_tristate()`, `cs53l30_set_dai_tdm_slot()`, and `cs53l30_mute_stream()`.

## Control Flow
I2C probe allocates private data, obtains/enables `VA` and `VP`, asserts reset, initializes regmap, reads the multi-byte Cirrus device ID through `cirrus_read_device_id()`, checks revision, gets optional `mclk` and `mute` GPIOs, programs mute-pin behavior and mic-bias/device-tree options, then registers the component. Component probe chooses either single-SDOUT or dual-SDOUT DAPM routes based on `cirrus,use-sdout2`. Runtime DAI setup first maps external MCLKX to internal MCLK division, then format selects master/slave, I2S or DSP_A/TDM, and SCLK inversion, and `hw_params()` maps `mclk_rate` plus sample rate to ASP rate and internal scaling.

## State and Persistence
State lives in the regmap cache (`REGCACHE_RBTREE`) and private fields for `mclk_rate`, `use_sdout2`, and GPIO handles. Bias-level transitions enable/disable the MCLK, clear low-power bits, wait for power stabilization, and on power-off poll `CS53L30_IS` for `PDN_DONE`, with a longer polling window when digital soft ramp is enabled. Runtime suspend switches regmap cache-only, holds reset low, and disables supplies; resume re-enables supplies, releases reset, disables cache-only, and syncs the cache.

## Dependencies and Integration Points
The driver depends on I2C, regmap, regulators, GPIO descriptors, optional common clock framework, ALSA SoC, TLV helpers, OF properties, and `cirrus_legacy.h` for ID reading. Device tree properties include `cirrus,micbias-lvl` and `cirrus,use-sdout2`; GPIO names are `reset` and `mute`; supplies are `VA` and `VP`; optional clock name is `mclk`.

## Risks and Edge Cases
`cs53l30_set_sysclk()` requires the external frequency to match one of the MCLKX coefficient entries before `hw_params()` can succeed. The TDM slot code treats ASoC slots as `slot_width` units but hardware slots as bytes, so slot width must be byte-aligned and no larger than 64 bits; it rejects more than four active channels and selections beyond hardware slot 47. `mute_stream()` calls `gpiod_set_value_cansleep()` unconditionally; this is safe only if NULL descriptors remain accepted by the GPIO helper. Runtime resume returns on regcache sync failure without disabling supplies again. The power-off poll loop has a suspicious condition `if (inter_max_check < 10)` after `inter_max_check` is set either to 10 or 90, so the short 1 ms branch is effectively unreachable.

## Test Signals
Test signals include probe logs showing revision, failure on wrong device ID, ALSA capture channel range 1-4, correct route differences with and without `cirrus,use-sdout2`, accepted/rejected sysclk-rate pairs, TDM slot register programming for byte-aligned slots, mute GPIO polarity behavior, and suspend/resume restoring modified controls through regcache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.h

## Purpose
`cs53l30.h` defines the register map, bitfields, reset defaults, interrupt masks, and TDM helper macros for the CS53L30 ADC codec driver. It is the hardware contract used by `cs53l30.c` for regmap defaults, controls, DAPM widgets, clocking, power, mute, and TDM programming.

## Important APIs, Types, and Constants
The header has no structs or function prototypes; its important exports are preprocessor constants. Register addresses cover device ID, power, MCLK, internal sample-rate control, mic bias, ASP/TDM controls, soft ramp, LRCK, mute pin controls, input bias controls, DMIC/ADC controls, ADC noise gate, analog front-end gain, digital volume, interrupt mask, and interrupt status. `CS53L30_TDM_SLOT_MAX`, `CS53L30_ASP_TDMTX_CTL(x)`, and `CS53L30_ASP_TDMTX_ENx(x)` support the C file's slot-location and byte-enable loops. `CS53L30_DEVID` is the expected device identity value.

## State and Persistence
The header defines default values used to seed the regmap cache, such as powered-down mic bias defaults, MCLK divider default, internal FS ratio default with reserved bits, ASP default as I2S/TDM powered down, input bias VCM defaults, DMIC stereo defaults, ADC/DMIC power defaults, HPF enabled by default, and full interrupt mask. These values become the baseline restored by regcache after runtime suspend.

## Dependencies and Integration Points
The file is consumed by the CS53L30 codec implementation. Its constants map directly to ASoC controls and DAPM power bits, so user-visible mixer names in the C file rely on these masks being correct. Platform integration must match the register-level assumptions here for mic-bias level, SDOUT routing, TDM slot capacity, and interrupt status semantics.

## Risks and Edge Cases
There are two notable macro issues. `CS53L30_IN3M_BIAS_MASK` shifts by `CS53L30_IN4M_BIAS_SHIFT` instead of `CS53L30_IN3M_BIAS_SHIFT`; current code only uses the default value macros, so the bug may be latent unless future code updates this field with the mask. `CS53L30_MUTE_ASP_SDOUTx_PDN` references `x` but is defined without a parameter; it is not used by current code, but it would fail or miscompile if used. The TDM enable register helper numbers registers in reverse order with `CS53L30_ASP_TDMTX_EN6 - x`, which must remain aligned with the datasheet's byte-enable layout.

## Test Signals
Compile tests should catch any future use of the malformed `CS53L30_MUTE_ASP_SDOUTx_PDN` macro. Regmap-default tests should compare defaults against datasheet reset values. TDM tests should verify that active slots are written to `ASP_TDMTX_CTL1..4` and byte-enable bits land in the expected reversed `ASP_TDMTX_EN` registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs53l30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.c

## Purpose
`cx20442.c` is an ASoC platform codec driver for the CX20442-11 voice modem codec. Unlike normal register-mapped codecs, it maps a one-byte pseudo power register to V.253 AT voice commands sent through a TTY line discipline. It provides a mono 8 kHz playback/capture DAI, DAPM paths for telephone, microphone, speaker, and AGC paths, and exports `v253_ops` so a machine driver can bind modem TTY traffic to the codec.

## Important APIs, Types, and Functions
`struct cx20442_priv` stores the active TTY, POR regulator, and pseudo register cache. `cx20442_read_reg_cache()` returns the cached pseudo register. `cx20442_write()` validates pseudo register writes, converts DAPM power bits to V.253 `+VLS` and `+VSP` command values, and writes only necessary modem commands. `cx20442_pm_to_v253_vls()` and `cx20442_pm_to_v253_vsp()` encode the allowed combinations of telephone line, microphone, speaker, and AGC power bits. `v253_open()`, `v253_close()`, `v253_hangup()`, and `v253_receive()` implement the exported line discipline callbacks.

## Control Flow
Platform probe registers the component and DAI. Component probe allocates private state, gets the `POR` regulator, initializes the TTY pointer to NULL, and sets card `pop_time` to zero until the modem is ready. A machine driver must arrange for `tty->disc_data` to point at the component before the V.253 line discipline opens. On open, the line discipline sends the initialization command `ate0m0q0+fclass=8\r`; the first received modem response then stores the TTY pointer and enables a small pop time. DAPM power changes write pseudo register bit combinations, which are converted to AT command strings such as `at+vls=...` and `at+vsp=...`.

## State and Persistence
The only codec state is volatile memory: cached pseudo register, live TTY pointer, and regulator handle. There is no hardware regmap cache. Bias transitions enable the POR regulator when moving from standby to prepare and disable it when returning from prepare to standby. Remove hangs up the TTY if still attached, releases the regulator, clears drvdata, and frees private memory.

## Dependencies and Integration Points
The driver depends on ASoC component/DAPM, the TTY subsystem, and regulators. Integration is platform-specific: a board/machine driver must register or reuse `v253_ops`, attach the line discipline to the modem TTY, set `disc_data` to the codec component, and provide the `cx20442-codec` platform device plus `POR` regulator. The DAI supports one channel each direction at 8 kHz S16_LE.

## Risks and Edge Cases
ASoC writes fail with `-EIO` until the line discipline has received a modem response and installed `cx20442->tty`. `cx20442_write()` updates `reg_cache` before validating VLS/VSP mappings, so an invalid write can leave cache state ahead of actual hardware command state. There is no explicit locking around TTY pointer/cache access between line discipline callbacks and ASoC DAPM writes. Unsupported power combinations return `-EINVAL`, and partial TTY writes return `-EIO`. Probe converts missing non-DT regulator `-ENODEV` to `-EPROBE_DEFER`, so board regulator constraints can affect startup.

## Test Signals
Important tests include line-discipline open with and without `disc_data`, modem init write length, first receive enabling codec TTY access, DAPM path toggles producing expected `+VLS`/`+VSP` commands, rejection of invalid path combinations, POR regulator enable/disable on bias transitions, and clean TTY hangup on component removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.h

## Purpose
`cx20442.h` is a minimal integration header for the CX20442 voice modem codec driver. Its only runtime contract is the exported V.253 TTY line discipline operations object.

## Important APIs and Types
The single declaration is `extern struct tty_ldisc_ops v253_ops;`. Machine or board code can use this symbol to register or delegate line discipline behavior while still allowing the codec driver to run its open, close, hangup, and receive callbacks.

## State and Persistence
The header defines no state. All state is in `cx20442.c` private data and in the TTY instance that carries `disc_data`.

## Dependencies and Integration Points
The declaration depends on `struct tty_ldisc_ops`, which is defined by the Linux TTY layer. Users of this header need the appropriate TTY headers in their own compilation unit. The symbol is exported by `cx20442.c` with `EXPORT_SYMBOL_GPL`, so GPL-compatible machine code can link to it.

## Risks and Edge Cases
Because the header only exposes a global line-discipline ops object, integration remains implicit: callers must know to set `tty->disc_data` to the ASoC component before opening the line discipline. There is no typed helper or wrapper enforcing that contract.

## Test Signals
Build tests should verify the exported `v253_ops` symbol resolves for machine drivers. Runtime validation belongs with `cx20442.c`: line discipline attachment must call into the codec callbacks and establish TTY-backed codec writes after the first modem response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx20442.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.c

## Purpose
`cx2072x.c` is an ASoC I2C driver for Conexant CX20721/CX20723 codecs. It provides HDA-style register access over I2C, codec initialization, PLL and I2S/PCM configuration, playback/capture/AEC DAIs, DAPM topology for ports and converters, mixer controls, runtime PM for MCLK, and platform-specific headset/button detection.

## Important APIs, Types, and Functions
`struct cx2072x_priv` stores regmap, MCLK, cached MCLK rate, component pointer, jack GPIO descriptor data, mutex, BCLK ratio, pending PLL/I2S reconfiguration flags, sample/frame sizes, sample rate, DAI format, and AEC-reference state. Custom regmap access is implemented by `cx2072x_register_size()`, `cx2072x_reg_raw_write()`, `cx2072x_reg_write()`, and `cx2072x_reg_read()` because registers are 1, 2, or 4 bytes wide under a 16-bit address. Clocking is handled by `cx2072x_config_pll()` and `cx2072x_config_i2spcm()`. DAI operations are `set_sysclk`, `set_fmt`, `hw_params`, and `set_bclk_ratio`. Jack support is implemented by `cx2072x_set_jack()`, `cx2072x_enable_jack_detect()`, and `cx2072x_jack_status_check()`.

## Control Flow
I2C probe allocates state, initializes custom regmap, reads vendor/revision IDs, obtains MCLK, sets initial dirty flags, registers three DAIs, and enables runtime PM. Component probe powers the AFG, writes a fixed register-init sequence, configures PortC and BIOS test bits, powers back down, and releases runtime PM. Audio setup stores format and MCLK rate first; `hw_params()` validates sample rate and frame/sample sizes, optionally enables AEC routing for the DSP DAI, then programs PLL and I2S/PCM registers if dirty flags are set. DAPM controls power DACs, ADCs, ports, muxes, and the AFG supply.

## State and Persistence
Register defaults are cached in an RBTREE regcache, but volatile ID, pin-sense, unsolicited-message, EQ band, and several test registers bypass cache. Runtime state for clocking is held in private fields and consumed during `hw_params()`. Runtime suspend disables MCLK; runtime resume prepares/enables it. Jack status is serialized by `cx2072x->lock` while reading pin sense/type registers and clearing the interrupt.

## Dependencies and Integration Points
The driver depends on I2C, regmap, common clock framework, runtime PM, ACPI matching, ALSA SoC, DAPM, jack GPIO helpers, and TLV controls. It matches I2C IDs `cx20721` and `cx20723`, and ACPI ID `14F10720`. Machine drivers use DAIs `cx2072x-hifi`, `cx2072x-dsp`, and `cx2072x-aec`; supported exposed rates are currently fixed at 48 kHz through `CX2072X_RATES_DSP`, though lower/higher rates are accepted in internal PLL validation.

## Risks and Edge Cases
The file explicitly notes TDM is not implemented. `set_dai_fmt()` stores a new format but does not mark `i2spcm_changed`, so a format change after the first `hw_params()` may not reprogram hardware unless another path sets the flag. `set_dai_bclk_ratio()` also stores a ratio without setting the reconfiguration flag. `cx2072x_config_pll()` ignores return values at its call site. The MCLK pre-divider table contains duplicate 36.864 MHz entries with different dividers, but the first match wins. Jack detection is hard-coded to specific ports/GPIO behavior and is called out as platform-specific. The component probe uses `pm_runtime_get_sync()` without checking failure status.

## Test Signals
Useful tests include vendor/revision read over custom I2C transfers, register-size coverage for 1/2/4-byte registers, PLL programming for supported sample rates and MCLKs, rejection of unsupported BCLK in master mode, DAPM powering of AFG/converters/ports, AEC DAI routing to ADC1 connection 3, runtime PM clock disable/enable, and jack reports for headphone, headset, and button states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.h

## Purpose
`cx2072x.h` defines the register addresses, DAI IDs, supported public rate macro, table-size constants, sample-size enum, and packed union layouts used by the CX20721/CX20723 codec driver. It provides the symbolic map for the driver's HDA-like register model and I2S/PCM control programming.

## Important APIs, Types, and Constants
Important constants include `CX2072X_REG_MAX`, vendor/revision registers, AFG/GPIO/UM registers, DAC/ADC converter/gain/power/stream registers, port pin/power/sense/EAPD/gain registers, mixer registers, EQ/DRC registers, I2S/PCM control registers, and analog/digital test registers. DAI IDs are `CX2072X_DAI_HIFI`, `CX2072X_DAI_DSP`, and `CX2072X_DAI_DSP_PWM`; the implementation also creates an AEC DAI with ID 3. `CX2072X_RATES_DSP` is currently `SNDRV_PCM_RATE_48000`.

## Register Layout Model
The packed unions `cx2072x_reg_i2spcm_ctrl_reg1` through `reg6` describe the bitfield layout used to build 32-bit I2S/PCM control writes: frame length, sample size, word-select polarity/width, slot numbers, master/slave flags, channel enables, pause cycles, and BCLK divider. `union cx2072x_reg_digital_bios_test2` defines PLL/I2S/EAPD pad-related bits. These unions are used in `cx2072x_config_i2spcm()` to avoid open-coded bit shifts for complex 32-bit registers.

## State and Persistence
The header has no allocated state, but its register definitions are the basis for the regmap cache defaults in the C file. Some constants are currently declared for future EQ/DRC/class-D extensions and are not actively used.

## Dependencies and Integration Points
The header relies on ALSA PCM rate macros being available before inclusion. It is included by `cx2072x.c` and should stay synchronized with that file's custom register-size function; adding a register address here without updating size/readable/volatile handling may produce broken I2C transfers or cache behavior.

## Risks and Edge Cases
The bitfield unions rely on C bitfield layout assumptions within the target kernel/compiler environment. The C file writes `ulval` directly after assigning fields, so changes to field order or type width would change hardware programming. `CX2072X_MCLK_PLL` and `CX2072X_MCLK_EXTERNAL_PLL` both equal 1, which may be intentional aliasing but offers no distinction if future code switches on both. The header exposes many test-register addresses, making it easy to cargo-cult platform-specific sequences into generic paths.

## Test Signals
Build tests should cover union field use and DAI ID references. Runtime tests should compare generated `I2SPCM_CONTROL*` values against expected datasheet bit layouts for I2S, left-justified, right-justified, clock-provider, BCLK inversion, and AEC-reference cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cx2072x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7210.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7210.c

## Purpose
`da7210.c` is an ASoC codec driver for the Dialog DA7210, supporting both I2C and SPI control buses. It defines the full register/bitfield map inline, exposes playback/capture controls, builds DAPM input/output/mixer routes, configures DAI word length/format/clocking/PLL, applies bus-specific register patches, and registers one stereo playback/capture DAI.

## Important APIs, Types, and Functions
`struct da7210_priv` stores the regmap, selected MCLK rate, and DAI master/slave state. `da7210_put_alc_sw()` and `da7210_put_noise_sup_sw()` enforce hardware constraints between ALC and noise suppression controls. `da7210_hw_params()` configures DAI source/output enable, sample width, sample-rate code, PLL bypass/SRM behavior, and active mode. `da7210_set_dai_fmt()` selects master/slave and I2S/left/right-justified format with fixed 64-bit frame length. `da7210_set_dai_sysclk()` validates supported MCLKs. `da7210_set_dai_pll()` programs divider registers from the static divider table. Bus probes initialize regmap, apply hidden/test register patches, and register the component.

## Control Flow
Module init registers the I2C driver when enabled and the SPI driver when enabled; module exit unregisters both. Each bus probe allocates private data, initializes a regmap with 8-bit register/value format, applies a patch sequence, and calls `devm_snd_soc_register_component()`. Component probe initializes the codec into a broadly enabled baseline: regulator and bias, mic PGAs/bias, input PGAs, ADCs, DAC source and enable bits, output PGAs, headphone, ramp mode, line outputs, aux inputs, PLL bypass, default 48 kHz PLL FS, and startup master enable. DAPM then controls standby bits for individual analog blocks.

## State and Persistence
The driver uses an RBTREE regcache with defaults for page/control, analog/digital audio registers, PLL registers, and ALC registers. `DA7210_STATUS` is volatile; several hidden unlock/test registers are marked unreadable. Runtime state for clocking is only `mclk_rate` and `master`; there is no runtime PM implementation. Bus-specific patches unlock hidden registers to configure PLL/charge-pump behavior, then relock them; SPI additionally performs dummy AUX2 writes and page switching.

## Dependencies and Integration Points
The driver depends on ASoC, regmap, I2C, SPI, PCM params, and TLV helpers. It matches I2C ID `da7210` and SPI driver name `da7210`. Machine drivers use DAI `da7210-hifi` with 1-2 playback/capture channels, rates 8 kHz through 96 kHz, and S16/S20_3LE/S24/S32 formats. It expects MCLK values from a fixed list: 12, 13, 13.5, 14.4, 19.2, 19.68, or 19.8 MHz.

## Risks and Edge Cases
`da7210_set_dai_fmt()` rejects format changes while PLL is enabled and not bypassed. PLL divider support is table-limited and in slave mode forces `fout` to 2.8224 MHz. Noise suppression enable is rejected unless ALC is disabled, zero-cross is enabled for HP/AUX1, and INPGA/AUX1 gains exceed thresholds; this is correct but can surprise users toggling controls in arbitrary order. Probe writes many blocks enabled up front and relies on DAPM standby bits for pop-free control. The comments contain several old FIXME notes: only fixed 64-bit frame length is supported, and historical format support was limited even though current switch accepts I2S/left/right justified.

## Test Signals
Test coverage should include I2C and SPI probe paths, patch application warnings, default mixer control visibility, ALC/noise-suppression mutual exclusion, hw_params for each supported width/rate, PLL table hit/miss behavior for master and slave mode, mute toggling through `DA7210_DAC_HPF`, DAPM route power for mic/aux/ADC/DAC/headphone/line/mono outputs, and module init cleanup when only one bus type is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7210.c -->
