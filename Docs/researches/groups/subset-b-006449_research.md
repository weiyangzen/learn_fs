# subset-b-006449 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359.h

## Purpose

`mt6359.h` is the private interface and register map for the MediaTek MT6359 ASoC codec driver. It gives `mt6359.c`, MT6359 accessory-detection code, and MediaTek machine drivers the symbolic addresses, bit shifts, masks, mux values, supply sequencing constants, runtime state shape, and exported helper prototypes needed to operate the PMIC audio codec. The file is not an implementation unit, but it is a high-risk hardware contract: most runtime behavior in the codec is implemented as `regmap_update_bits()` calls using the names defined here.

The header covers several hardware blocks:

- PMIC top, GPIO, clock, reset, and LDO registers used to route MTKAIF pins and keep audio clocks alive during calibration.
- Audio top and digital AFE registers for UL/DL enable, MTKAIF protocol, sync words, FIFOs, async FIFOs, sine generators, and monitor signals.
- Audio encoder analog registers for ADCs, preamps, mic bias, DCC, digital microphones, accessory-detection analog routing, and EINT comparators.
- Audio decoder analog registers for DAC, headphone, receiver, line-out, bias, LDO, NCP, zero-cross detection, and gain ramps.
- Accessory-detection register fields for PWM timing, debounce, FSM state, EINT state, IRQ clear/status, moisture detect, and monitor flags.

## Important APIs, Types, and Constants

Important public-to-driver constants include:

- `CODEC_MT6359_NAME`, the ASoC component name used by the codec component driver.
- `MT6359_MAX_REGISTER`, currently `MT6359_ZCD_CON5`, used by the regmap configuration in the implementation.
- `MT_SOC_ENUM_EXT_ID(...)`, a local helper macro for building mixer enum controls with an encoded device id.
- `IS_DCC_BASE(type)`, used to classify DCC microphone mux modes.

Important exported helper prototypes are:

- `mt6359_set_mtkaif_protocol(struct snd_soc_component *cmpnt, int mtkaif_protocol)`, used by MT8192/MT8188 machine drivers to select MTKAIF protocol 1, protocol 2, or protocol 2 clock P2.
- `mt6359_mtkaif_calibration_enable(struct snd_soc_component *cmpnt)` and `mt6359_mtkaif_calibration_disable(...)`, used by machine drivers during boot-time MTKAIF phase calibration.
- `mt6359_set_mtkaif_calibration_phase(struct snd_soc_component *cmpnt, int phase_1, int phase_2, int phase_3)`, used to sweep and set pad phase values.

Important enums define codec state dimensions:

- `MT6359_MTKAIF_PROTOCOL_*` controls MTKAIF TX/RX register programming.
- `MT6359_AIF_1`, `MT6359_AIF_2`, and `MT6359_AIF_NUM` index per-DAI playback/capture rates.
- `AUDIO_ANALOG_VOLUME_*` indexes persistent analog gain values for headset, headphone, line-out, and three mic amps.
- `MUX_*`, `DEVICE_*`, `HP_GAIN_CTL_*`, `HP_MUX_*`, `RCV_MUX_*`, and `LO_MUX_*` describe mixer routes and powered endpoint counters.
- `SUPPLY_SEQ_*` names DAPM supply subsequences; these encode ordering assumptions for clocks, global bias, top clocks, NCP, AFE, playback, and capture paths.
- `MIC_BIAS_*`, `DL_GAIN_*`, `MIC_TYPE_MUX_*`, `UL_SRC_MUX_*`, `MISO_MUX_*`, `DMIC_MUX_*`, `ADC_MUX_*`, and `PGA_*_MUX_*` are user-visible or route-control values consumed by mixer controls and event handlers.

`struct mt6359_priv` is the main runtime state owned by `mt6359.c`. It stores the device and regmap, playback and capture rates per AIF, analog gains, mux selections, one-wire DMIC mode, per-device power counters, headphone gain control mode, headphone hi-fi mode, and the selected MTKAIF protocol.

## Control Flow and Behavioral Role

This header shapes control flow indirectly. DAPM event handlers and mixer callbacks in `mt6359.c` use the register and mask constants to sequence hardware:

1. Probe obtains the parent MT6397/PMIC regmap, allocates `struct mt6359_priv`, parses device tree, initializes the component regmap, and registers DAIs named by the implementation.
2. Machine-driver init calls `mt6359_set_mtkaif_protocol()` and calibration helpers. These helpers use `MT6359_GPIO_MODE*`, `MT6359_AFE_ADDA_MTKAIF_CFG0`, `MT6359_AFE_AUD_PAD_TOP`, `MT6359_AUDIO_DIG_CFG`, and `MT6359_AUDIO_DIG_CFG1` constants from this header to switch pins, enable loopback, and tune phase.
3. Playback DAPM paths use `SUPPLY_SEQ_*`, HP/RCV/LO mux enums, gain enums, ZCD registers, NCP registers, LDO/NV registers, and decoder analog fields to ramp outputs and avoid pops.
4. Capture DAPM paths use mic-bias, PGA, ADC, DCC, DMIC, UL source, MTKAIF, and MISO mux constants to select analog/digital microphone paths and enable clocks.
5. Accessory detection uses the ACCDET and EINT register groups to configure debounce, PWM, IRQ, state reads, AUXADC interaction, and moisture/plug state.

Because there is no executable code in this header, there are no local branches or loops. The effective control flow lives in clients that apply these constants.

## State and Persistence

Hardware state persists in PMIC registers, not in this header. `struct mt6359_priv` mirrors selected runtime policy and cached ALSA control state:

- `dl_rate[]` and `ul_rate[]` persist selected sample rates while streams are active.
- `ana_gain[]` persists ALSA analog gain settings so events can restore gain during ramps.
- `mux_select[]` persists selected route control values.
- `dev_counter[]` tracks shared endpoint use to avoid disabling hardware still needed by another route.
- `mtkaif_protocol`, `hp_gain_ctl`, `hp_hifi_mode`, and `dmic_one_wire_mode` persist board/runtime policy.

The register definitions also encode persistent hardware latch semantics: `_SET` and `_CLR` registers are side-effect write ports, interrupt clear bits are write-to-clear style, and monitor/status fields are read-only hardware state. A client using the wrong `_SET`/`_CLR` or status symbol can leave clocks, resets, or IRQs latched incorrectly.

## Dependencies and Integration Points

The header depends on ASoC declarations being visible to clients because it declares `struct snd_soc_component` helper prototypes and uses ALSA control structures in `MT_SOC_ENUM_EXT_ID`. It also assumes Linux `BIT()` is available through including C files.

Important integration points are:

- `sound/soc/codecs/mt6359.c`, the main consumer of almost all audio register, enum, and private-state definitions.
- `sound/soc/codecs/mt6359-accdet.*`, which consumes the ACCDET, AUXADC, mic-bias, EINT, and IRQ field definitions.
- MediaTek machine drivers such as MT8192 and MT8188, which include this header to call MTKAIF protocol and calibration helpers and to bind codec DAIs named by the MT6359 component.
- The parent PMIC/MFD driver, because the codec operates through the shared MT6397 regmap rather than its own bus.

## Risks and Edge Cases

- The header contains duplicated symbolic address definitions: an early minimal register block and a later fuller "audio register" block repeat several `MT6359_*` names. This is legal when values match, but it increases maintenance risk and can hide accidental divergence in future edits.
- Some early field macros refer to register names defined later, such as `MT6359_AUD_TOP_RST_BANK_CON0` and `MT6359_AUD_TOP_INT_RAW_STATUS0`. C preprocessing tolerates this, but readers must not assume definitions are strictly topological.
- A likely typo exists in the early `AUXADC_ACCDET_ANASWCTRL_EN_ADDR` macro: it references `MT6359_AUXADC_CON15`, while the top-level block shown in this header defines `MT6359_AUXADC_CON10` and `MT6359_AUXADC_ACCDET`; no `MT6359_AUXADC_CON15` definition appears in this file. Any client expanding that macro would fail to compile unless another include supplies it.
- `MT6359_MAX_REGISTER` is set to `MT6359_ZCD_CON5`, while this header defines ACCDET registers above that address. That can be correct if the main codec regmap intentionally excludes ACCDET, but it is a risk if shared regmap readability/writeability is expected for the full header map.
- Register bit fields are highly sensitive to datasheet revisions. A wrong shift or mask can create silent audio failures, pop noise, stuck IRQs, or excess idle current.
- `struct mt6359_priv` is private but shared through the header. Any layout change affects all code compiled against the codec implementation.

## Test Signals

Useful validation signals include:

- Build coverage for `SND_SOC_MT6359`, `SND_SOC_MT6359_ACCDET`, and MediaTek machine drivers that include this header.
- `dtbs_check` and probe logs for MT8188/MT8192 boards using `mt6359-sound` and MTKAIF calibration.
- Playback smoke tests over headphone, receiver, line-out, and speaker-linked routes, checking DAPM sequencing and idle-current return after close.
- Capture tests over analog mic, DCC mic, ECM single/differential, and DMIC routes, including one-wire DMIC policy.
- Jack insertion/removal, button, moisture/EINT, and AUXADC accdet tests with IRQ clear/status verification.
- Suspend/resume tests confirming cached software state and PMIC register state remain consistent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.c

## Purpose

`mt6660.c` implements the MediaTek/Richtek MT6660 smart speaker amplifier codec as an I2C ASoC component. It provides custom regmap access for variable-width MT6660 registers, initializes the amplifier hardware, exposes ALSA mixer controls, defines DAPM widgets/routes for playback and voltage/current capture, handles DAI hardware parameters, and integrates runtime PM with the chip low-power bit.

The driver registers a single DAI named `mt6660-aif` with playback stream `aif_playback` and capture stream `aif_capture`. Playback drives the DAC/PGA/ClassD path and capture exposes the VI ADC connected to the ClassD output.

## Important APIs, Types, and Functions

Important local types:

- `struct reg_size_table` maps selected register addresses to 2-byte or 4-byte register widths. Unlisted registers default to one byte.
- `struct reg_table` stores init-sequence address/mask/value triples.
- `struct mt6660_chip`, declared in `mt6660.h`, stores the I2C client, device, regmap, mutex, platform-data holder, and chip revision.

Important functions:

- `mt6660_get_reg_size()` chooses the I2C transfer width for a register.
- `mt6660_reg_write()` and `mt6660_reg_read()` are custom regmap bus callbacks that marshal big-endian byte arrays through SMBus block read/write.
- `mt6660_codec_dac_event()` inserts a 1 ms delay after DAC power-up.
- `mt6660_codec_classd_event()` sequences boost mode, voltage sensing, pop-noise mitigation, and off mode around ClassD DAPM power events.
- `mt6660_component_get_volsw()` exposes the low nibble of `chip_rev` as a read-only-ish ALSA control named `Chip Rev`.
- `_mt6660_chip_power_on()` writes bit 0 of `MT6660_REG_SYSTEM_CTRL`, using `0` for on and `1` for low power/off.
- `mt6660_component_setting()` powers the chip, applies `mt6660_setting_table`, then powers it down.
- `mt6660_component_aif_hw_params()` programs serial audio bit depth and TDM word length from ALSA hardware parameters.
- `_mt6660_chip_id_check()`, `_mt6660_chip_sw_reset()`, and `_mt6660_read_chip_revision()` validate and initialize the device during probe.
- `mt6660_i2c_probe()`, `mt6660_i2c_remove()`, `mt6660_i2c_runtime_suspend()`, and `mt6660_i2c_runtime_resume()` are the I2C driver lifecycle and PM hooks.

Important ALSA objects:

- `mt6660_component_snd_controls` exposes digital volume, hard clip, clip, boost mode, DRE, DC protect, data output channel selection, T0 selection, and chip revision.
- DAPM widgets define `DAC`, `VI ADC`, `PGA`, `ClassD`, `OUTP`, and `OUTN`.
- DAPM routes connect `aif_playback -> DAC -> PGA -> ClassD -> OUTP/OUTN` and `ClassD -> VI ADC -> aif_capture`.

## Control Flow

Probe flow:

1. `mt6660_i2c_probe()` allocates `struct mt6660_chip`, stores I2C/device pointers, initializes `io_lock`, attaches client data, and creates a regmap with custom read/write callbacks.
2. `_mt6660_chip_sw_reset()` writes `SYSTEM_CTRL` first to `0x00`, then `0x80`, and sleeps 30 ms.
3. `_mt6660_chip_power_on(chip, 1)` clears bit 0 so the chip leaves low-power mode.
4. `_mt6660_chip_id_check()` reads `DEVID`, masks `0x0ff0`, and accepts `0x00e0` or `0x01e0`.
5. `_mt6660_read_chip_revision()` saves `DEVID & 0xff`.
6. Runtime PM is marked active/enabled, then `devm_snd_soc_register_component()` registers the component and DAI.
7. On failure after reset/power-on, the chip is powered off and the mutex destroyed.

Component flow:

1. `mt6660_component_probe()` binds the chip regmap to the ASoC component.
2. `mt6660_component_setting()` powers the chip on, applies the hard-coded init table with `snd_soc_component_update_bits()`, and powers the chip off.
3. `mt6660_component_remove()` detaches the component regmap.

Stream flow:

1. ALSA `hw_params` calls `mt6660_component_aif_hw_params()`.
2. The driver rejects physical word lengths outside 16 to 32 bits.
3. It maps audio sample width to `SERIAL_CFG1[7:6]` and writes physical word length to `TDM_CFG3[9:4]`.
4. DAPM powers the DAC, waits 1 ms post-PMU, and powers ClassD through pre/post PMU and PMD transitions.

Runtime PM flow:

- Suspend sets `SYSTEM_CTRL[0]` to `1`.
- Resume clears `SYSTEM_CTRL[0]` to `0`.

## State and Persistence

The driver keeps minimal software state in `struct mt6660_chip`. `chip_rev` persists the hardware revision read at probe and backs the `Chip Rev` mixer control. The regmap itself has custom callbacks but no explicit cache policy in this file.

Hardware state persists in MT6660 registers. The init table writes many reserved, protection, HPF, signal, gain, boost, and DRE fields. Runtime stream state is mostly represented by ASoC DAPM-managed register bits, ALSA control writes, and runtime PM writes to `SYSTEM_CTRL`.

The `io_lock` mutex is initialized and destroyed but not used by the custom register callbacks in the current file. If future multi-byte register access requires serialization beyond regmap's own locking, that mutex may be intended for expansion.

## Dependencies and Integration Points

The driver depends on:

- Linux I2C SMBus block operations.
- Linux regmap with custom `.reg_read` and `.reg_write` callbacks.
- ASoC component, DAI, DAPM, TLV, and PCM params APIs.
- Runtime PM helpers through `RUNTIME_PM_OPS`.
- `mt6660.h` register and state declarations.

Board integration uses an I2C device id `mt6660` or an OF compatible string `mediatek,mt6660`. Machine drivers must connect to the DAI name `mt6660-aif` and provide the required clock/data format through normal ASoC links.

## Risks and Edge Cases

- `mt6660_get_reg_size()` defaults all unlisted registers to one byte. If a multi-byte register is omitted from `mt6660_reg_size_table`, reads and writes will silently truncate or update the wrong width.
- The custom SMBus block callbacks encode/decode multi-byte values big-endian. This must match the chip protocol for every register width.
- The regmap is configured with `.val_bits = 32`, while the physical transfer size varies by address. ASoC controls that assume normal one-value register semantics depend on the custom callbacks doing the right width conversion.
- `_mt6660_chip_power_on()` uses inverse bit semantics: `on_off` true writes `0`, false writes `1`. This is easy to misuse.
- `mt6660_component_setting()` returns early if an init-table write fails after powering the chip on, without powering it back off in that error path.
- Runtime PM is enabled only after chip id/revision succeeds. On later component registration failure, PM is disabled, but the chip may remain powered from earlier probe flow.
- `SOC_SINGLE_EXT("T0 SEL", ..., snd_soc_get_volsw, NULL)` has a getter and no setter, making it effectively read-only despite the control name not saying so.

## Test Signals

Useful validation signals include:

- Kernel build with the MT6660 codec enabled and no sparse warnings around regmap callback signatures.
- I2C probe logs showing reset, accepted device id, and revision.
- Regmap read/write tracing for 1-byte, 2-byte, and 4-byte registers, especially `DEVID`, `TDM_CFG3`, `HCLIP_CTRL`, `DA_GAIN`, and HPF coefficients.
- Playback tests at 16, 20, 24, and 32 bit widths and physical word lengths from 16 to 32 bits.
- Capture tests for the VI ADC path while ClassD is active.
- DAPM start/stop tests checking boost mode, voltage sensing, and pop-noise bits return to expected values.
- Runtime suspend/resume tests confirming `SYSTEM_CTRL[0]` transitions and audio resumes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.h

## Purpose

`mt6660.h` is the private companion header for the MT6660 smart speaker amplifier driver. It declares the driver-owned platform and chip state structures and assigns symbolic names to MT6660 register addresses used by `mt6660.c`.

The header is intentionally small compared with the implementation. It does not define masks for most fields; the C file uses literal masks and values for component controls, DAPM events, hardware-parameter programming, reset, power, and init sequencing.

## Important APIs, Types, and Constants

Important structures:

- `struct mt6660_platform_data` stores an optional init-setting table shape: count plus parallel arrays of addresses, masks, and values. In the current implementation this field is present in `struct mt6660_chip` but not populated or consumed.
- `struct mt6660_chip` is the main driver state. It includes `struct i2c_client *i2c`, `struct device *dev`, an optional `param_dev`, embedded platform data, an `io_lock` mutex, a `struct regmap *regmap`, and `u16 chip_rev`.

Important register constants include:

- Identity and power: `MT6660_REG_DEVID`, `MT6660_REG_SYSTEM_CTRL`.
- Interrupt/clock/serial path: `MT6660_REG_IRQ_STATUS1`, `MT6660_REG_ADDA_CLOCK`, `MT6660_REG_SERIAL_CFG1`, `MT6660_REG_TDM_CFG3`.
- Data path and filters: `MT6660_REG_DATAO_SEL`, `MT6660_REG_HPF_CTRL`, `MT6660_REG_HPF1_COEF`, `MT6660_REG_HPF2_COEF`, `MT6660_REG_PATH_BYPASS`.
- Protection, gain, and processing: `MT6660_REG_WDT_CTRL`, `MT6660_REG_HCLIP_CTRL`, `MT6660_REG_VOL_CTRL`, `MT6660_REG_SPS_CTRL`, `MT6660_REG_SIGMAX`, `MT6660_REG_CALI_T0`, `MT6660_REG_BST_CTRL`, `MT6660_REG_PROTECTION_CFG`, `MT6660_REG_DA_GAIN`, `MT6660_REG_SIG_GAIN`, `MT6660_REG_DRE_CTRL`, `MT6660_REG_DRE_THDMODE`, `MT6660_REG_DRE_CORASE`, `MT6660_REG_PWM_CTRL`, `MT6660_REG_DC_PROTECT_CTRL`.
- Misc/reserved tuning registers: `MT6660_REG_RESV0` through selected `RESV40` symbols.

## Control Flow and Behavioral Role

This header has no direct control flow. Its structure definitions and register symbols support `mt6660.c` flows:

1. Probe allocates `struct mt6660_chip`, initializes `io_lock`, stores I2C and device pointers, and creates the custom regmap.
2. Custom regmap accessors use the register constants to select byte widths for multi-byte registers.
3. Reset, power, id-check, revision-read, DAPM event handling, mixer controls, and hardware-parameter setup all refer to these register names.
4. Component and DAI registration expose the state to ASoC through `snd_soc_component_get_drvdata()`.

## State and Persistence

`struct mt6660_chip` stores all driver-local persistent state. `chip_rev` is read once from `MT6660_REG_DEVID` and exposed through a mixer control. The platform-data arrays could persist board-specific init values, but this version of the C driver uses a hard-coded `mt6660_setting_table` instead.

The hardware registers named here retain runtime state for low-power mode, serial format, DSP features, output selection, boost mode, protection, and gain. Because the header provides addresses but not typed field helpers, the implementation relies on literal masks, which makes field-level persistence harder to audit.

## Dependencies and Integration Points

The header depends on Linux mutex and regmap declarations. It is included by `mt6660.c`; it is not a public UAPI header.

Integration points are:

- Linux I2C, because `struct mt6660_chip` stores the client and custom callbacks call SMBus block operations.
- ASoC component/DAI code in `mt6660.c`, which uses this state via component driver data.
- Device tree or I2C board info binding to instantiate the `mt6660` I2C driver.

## Risks and Edge Cases

- The structures are wrapped in `#pragma pack(push, 1)`. Packing a structure containing pointers, a mutex, and a regmap pointer is unusual in kernel driver code and may create alignment penalties or architecture-sensitive behavior. There is no wire-format need visible in this file.
- `struct mt6660_platform_data` uses raw pointer arrays with no ownership or lifetime rules documented. If future code consumes these, it must validate `init_setting_num` against all arrays.
- `param_dev` is declared but unused in the implementation, suggesting either incomplete platform-data support or a removed feature.
- Register constants include many `RESV*` names. They are used in the init table and DAPM event path; datasheet drift or silicon revision differences could require guarded programming.
- Lack of field-specific masks in the header makes it easier for the C file to use inconsistent literal masks.

## Test Signals

Useful validation signals include:

- Compiler coverage on strict-alignment architectures, watching for packed-structure issues.
- Probe tests confirming `struct mt6660_chip` can be safely allocated, initialized, and passed to regmap callbacks.
- Register access tests for every address listed in the C file's variable-width table.
- Static review comparing literal masks in `mt6660.c` with the register definitions here.
- Any future platform-data support should add tests for array count validation and ownership.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8315.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8315.c

## Purpose

`nau8315.c` implements a minimal ASoC platform driver for the Nuvoton NAU8315/NAU8318 mono Class-D amplifier. The device has no register bus in this driver; control is through an optional GPIO named `enable` plus ASoC DAPM and PCM trigger events. The driver registers one playback-only DAI named `nau8315-hifi`.

## Important APIs, Types, and Functions

Important state:

- `struct nau8315_priv` stores `struct gpio_desc *enable` and `int enpin_switch`. `enable` is optional; `enpin_switch` records whether the DAPM `EN_Pin` output driver is logically powered.

Important functions:

- `nau8315_daiops_trigger()` receives PCM trigger commands. On start/resume/pause-release it asserts the enable GPIO only if `enpin_switch` is set. On stop/suspend/pause-push it deasserts the GPIO.
- `nau8315_enpin_event()` updates `enpin_switch` on `SND_SOC_DAPM_PRE_PMU` and `SND_SOC_DAPM_POST_PMD`.
- `nau8315_platform_probe()` allocates state, gets the optional enable GPIO as output low, stores driver data, and registers the component and DAI.

Important ASoC objects:

- DAPM widgets: `Speaker` output and `EN_Pin` output driver.
- DAPM routes: `HiFi Playback -> EN_Pin -> Speaker`.
- Component driver: sets widgets/routes, `idle_bias_on = 1`, `use_pmdown_time = 1`, and `endianness = 1`.
- DAI driver: playback stream `HiFi Playback`, 1 to 2 channels, 8 kHz to 96 kHz, formats `S16_LE` and `S24_3LE`.

## Control Flow

Probe flow:

1. Platform probe allocates `nau8315_priv` with `devm_kzalloc()`.
2. It requests optional GPIO `enable` using `devm_gpiod_get_optional(..., GPIOD_OUT_LOW)`, so the amp starts disabled.
3. It stores state with `dev_set_drvdata()`.
4. It registers the ASoC component and one DAI with devm lifetime management.

Stream and DAPM flow:

1. When the DAPM route to `Speaker` powers up, the `EN_Pin` widget receives `PRE_PMU` and sets `enpin_switch = 1`.
2. When PCM trigger receives start/resume/pause-release, the GPIO is driven high if an enable GPIO exists and the DAPM switch has been set.
3. On stop/suspend/pause-push, the GPIO is driven low.
4. When DAPM powers down, `POST_PMD` clears `enpin_switch`.

The split between DAPM and trigger means the GPIO only asserts when both the route is powered and the stream is actively running.

## State and Persistence

The only persistent software state is the optional GPIO descriptor and `enpin_switch`. There is no register cache, firmware state, or suspend callback. GPIO output state persists electrically until changed by trigger, probe initialization, device removal, or system GPIO handling.

Because devm resources are used, memory, GPIO, and component registration are automatically released with the platform device.

## Dependencies and Integration Points

The driver depends on:

- Linux platform-device infrastructure.
- gpiod consumer API for optional `enable`.
- ASoC component, DAI, DAPM, and PCM trigger APIs.
- OF compatible strings `nuvoton,nau8315` and `nuvoton,nau8318`.
- ACPI IDs `NVTN2010` and `NVTN2012`.

Board descriptions should provide an optional `enable-gpios` property if hardware requires GPIO gating. Machine drivers should route playback to DAI `nau8315-hifi` and stream name `HiFi Playback`.

## Risks and Edge Cases

- If `enable` is absent, trigger events become no-ops and the driver assumes the amplifier is always available or controlled externally.
- Unknown trigger commands fall through and return success. That is normal for many simple DAI ops, but it can hide unsupported state transitions.
- `enpin_switch` is an `int` modified by DAPM events and read by trigger callbacks without explicit locking. ASoC sequencing usually serializes these paths enough, but the variable is still a shared software gate.
- There is no explicit remove, shutdown, or suspend hook to force GPIO low. Stop/suspend trigger should do it for normal PCM paths, but abrupt unbind or system paths rely on devm/GPIO default behavior.
- The DAI advertises stereo support even though the amplifier is described as mono. That may be intentional for slot compatibility, but board routing must account for channel handling.

## Test Signals

Useful validation signals include:

- Probe on OF and ACPI instantiated devices, both with and without `enable-gpios`.
- GPIO scope or `gpioinfo` checks showing initial low, high on playback start, low on stop, and low on suspend/pause-push.
- DAPM route tests verifying `EN_Pin` only gates the GPIO when the speaker path is active.
- Playback smoke tests for 8 kHz to 96 kHz and `S16_LE`/`S24_3LE`.
- Repeated start/stop and pause/release tests to catch stale `enpin_switch` state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.c

## Purpose

`nau8325.c` implements the Nuvoton NAU8325 stereo Class-D amplifier as an I2C ASoC codec. It manages a 16-bit-address/16-bit-data regmap, exposes playback controls, performs reset and register initialization, selects internal clocking from MCLK and sample rate, configures serial audio format and sample width, and sequences mute/power DAPM events.

The driver registers one playback DAI named `nau8325-hifi` with stream name `Playback`, 1 to 2 channels, 8 kHz to 96 kHz, and `S16_LE`, `S20_3LE`, and `S24_3LE` formats.

## Important APIs, Types, and Functions

Important tables:

- `mclk_n1_div`, `mclk_n2_div`, and `mclk_n3_mult` define divider/multiplier selector encodings for deriving internal clock sources.
- `osr_dac_sel` maps DAC oversampling selector values to oversampling ratios and DAC clock source selectors.
- `target_srate_table` maps supported sample rates to clock-detection range bits, max/min policy, and valid MCLK source frequencies for 256, 400, and 500 fs ratios.
- `nau8325_reg_defaults` provides regcache defaults for the RBTREE regcache.

Important regmap helpers:

- `nau8325_readable_reg()`, `nau8325_writeable_reg()`, and `nau8325_volatile_reg()` describe which registers can be accessed and cached.
- `nau8325_regmap_config` uses 16 register bits, 16 value bits, `NAU8325_REG_MAX`, RBTREE cache, and those access callbacks.

Important ALSA controls:

- `DAC Oversampling Rate` enum for 64, 256, 128, and 32.
- `Speaker Volume` stereo TLV control over `NAU8325_R13_DAC_VOLUME`.
- ALC controls for max gain, min gain, decay, attack, hold, target level, and enable.

Important runtime functions:

- `nau8325_dac_event()` soft-unmutes after DAC power-up and soft-mutes before DAC power-down, sleeping 30 ms in both cases.
- `nau8325_powerup_event()` toggles `NAU8325_PWRUP_DFT` when clock-detection policy requires software power-up control.
- `nau8325_srate_clk_apply()`, `nau8325_clksrc_n2()`, `target_srate_attribute()`, `nau8325_clksrc_choose()`, and `nau8325_clock_config()` derive and write clock tree settings.
- `nau8325_get_osr()`, `nau8325_dai_startup()`, and `nau8325_hw_params()` constrain rates and program OSR, clock config, and audio word length.
- `nau8325_set_fmt()` programs I2S/left/right/DSP A/B format and bit-clock inversion, accepting only codec-slave mode.
- `nau8325_set_sysclk()` stores the board-provided MCLK after range checking.
- `nau8325_reset_chip()`, `nau8325_software_reset()`, `nau8325_init_regs()`, `nau8325_read_device_properties()`, and `nau8325_i2c_probe()` handle probe-time setup.

## Control Flow

Probe flow:

1. `nau8325_i2c_probe()` uses platform data if provided; otherwise it allocates `struct nau8325` and reads device properties.
2. It stores client data and initializes an I2C regmap with 16-bit register and value widths.
3. It stores `dev`, prints debug property values, performs hardware and software resets, and reads `NAU8325_R02_DEVICE_ID`.
4. It calls `nau8325_init_regs()` to program ALC defaults, clock detection/power policy, DAC reference voltage, VMID impedance, analog power bits, and default DAC oversampling.
5. It registers the ASoC component and DAI.

Clock and stream flow:

1. Machine driver calls component `.set_sysclk`, which validates MCLK between 2.048 MHz and 49.152 MHz and stores it in `nau8325->mclk`.
2. DAI startup reads current DAC OSR and constrains maximum sample rate to `CLK_DA_AD_MAX / osr`.
3. `hw_params` stores `fs`, validates `fs * osr <= 6.144 MHz`, writes DAC clock source from OSR, computes clock divisors/multipliers for the selected sample rate, and writes sample width bits.
4. `set_fmt` configures serial format. Only `SND_SOC_DAIFMT_CBC_CFC` is accepted; normal bit/frame polarity and inverted bit-clock with normal frame are accepted.
5. DAPM route `AIFRX -> DACL/DACR -> SPKL/SPKR` powers DACs and the `Power Up` supply, invoking soft mute and optional software power-up control.

## State and Persistence

`struct nau8325` stores:

- `mclk`, set by `.set_sysclk`.
- `fs`, set by `hw_params`.
- Device properties `vref_impedance_ohms`, `dac_vref_microvolt`, `clock_detection`, `clock_det_data`, and `alc_enable`.
- `dev` and `regmap` handles.

Register state persists in the chip and is cached by regmap except for volatile reset, ID/status/debug/readback registers. The driver does not implement explicit suspend/resume; it relies on ASoC bias/DAPM behavior and regcache defaults. DAPM mute state persists in `NAU8325_R12_MUTE_CTRL`.

Device properties define persistent board policy:

- `nuvoton,alc-enable`.
- `nuvoton,clock-det-data`.
- `nuvoton,clock-detection-disable`, inverted into `clock_detection`.
- `nuvoton,vref-impedance-ohms`, default 125000.
- `nuvoton,dac-vref-microvolt`, default 2880000.

## Dependencies and Integration Points

The driver depends on:

- Linux I2C and regmap.
- ASoC controls, component, DAI, DAPM, TLV, and PCM params APIs.
- Firmware property APIs for OF/ACPI-style properties.
- `nau8325.h` for all register and field definitions.

Device matching uses I2C id `nau8325` and OF compatible `nuvoton,nau8325`. Machine drivers must provide MCLK through `.set_sysclk`, choose a supported DAI format, and connect to DAI `nau8325-hifi`.

## Risks and Edge Cases

- Clock setup depends on `.set_sysclk` being called before `hw_params`. If `mclk` is zero, `nau8325_clksrc_choose()` fails and stream startup cannot complete.
- `nau8325_clksrc_choose()` exits the divider/multiplier search at the first valid candidate because it jumps to `proc_done` inside the nested loop, even though the condition tracks `mclk_max`. That makes the "max" search logic ineffective.
- `nau8325_read_device_properties()` sets `clock_detection = !device_property_read_bool(... "clock-detection-disable")`; debug output labels it as `clock-detection-disable`, which can confuse interpretation.
- `nau8325_init_regs()` writes ALC and clock-detection settings twice in similar blocks, increasing drift risk.
- Device ID is read but not validated against an expected value.
- Invalid `dac-vref-microvolt` or `vref-impedance-ohms` values only produce debug messages after defaults are applied only for absent properties. Present but invalid values leave the corresponding register field unchanged from reset/default.
- Regmap write errors in init and DAPM event helpers are mostly ignored; failures can leave the amp partially configured without failing probe or stream transitions.
- Supported DAI formats include only `S20_3LE` and `S24_3LE` for 20/24-bit packed samples, while `hw_params` has a 32-bit case that the DAI format mask does not advertise.

## Test Signals

Useful validation signals include:

- Probe with `nuvoton,nau8325`, confirming regmap creation and readable device ID.
- Board tests confirming `.set_sysclk` supplies one of the supported MCLK values for each target sample rate.
- Playback tests at 8, 12, 16, 24, 32, 44.1, 48, 64, and 96 kHz where board MCLK permits them.
- Format tests for I2S, left-justified, right-justified, DSP_A, and DSP_B, including bit-clock inversion.
- Mixer tests for DAC oversampling and ALC controls, followed by stream startup to verify rate constraints.
- DAPM power-cycle tests checking soft mute/unmute timing and `Power Up` behavior with clock detection enabled and disabled.
- Regmap cache/register dump checks after reset/init for reference voltage, VMID, ALC, analog enable, and oversampling fields.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.h

## Purpose

`nau8325.h` is the private register and state header for the NAU8325 ASoC amplifier driver. It defines the 16-bit register address map, bit masks and shifts for clocking, serial audio, mute, volume, ALC, clock detection, analog control, clipping, and DAC reference configuration. It also declares the driver state and small attribute structures used by `nau8325.c` for clock and oversampling selection.

## Important APIs, Types, and Constants

Important register constants:

- Reset and identity: `NAU8325_R00_HARDWARE_RST`, `NAU8325_R01_SOFTWARE_RST`, `NAU8325_R02_DEVICE_ID`.
- Clock and enable: `NAU8325_R03_CLK_CTRL`, `NAU8325_R04_ENA_CTRL`, `NAU8325_R40_CLK_DET_CTRL`.
- Interrupt and IO: `NAU8325_R05_INTERRUPT_CTRL`, `NAU8325_R06_INT_CLR_STATUS`, `NAU8325_R09_IRQOUT`, `NAU8325_R0A_IO_CTRL`.
- Digital audio interface: `NAU8325_R0B_PDM_CTRL`, `NAU8325_R0C_TDM_CTRL`, `NAU8325_R0D_I2S_PCM_CTRL1`, `NAU8325_R0E_I2S_PCM_CTRL2`, left/right time slots.
- Audio processing: HPF, mute, DAC volume, DAC oversampling, ALC controls.
- Analog and output: mixer, bias, analog control 1-6, clip control, and RDAC.

Important field groups:

- Clock source, multiplier, MCLK selector, and DAC source masks in `CLK_CTRL`.
- Left/right DAC enables in `ENA_CTRL`.
- Interrupt masks/disables for power, clip, low voltage, OCP/OTP, and ARP down.
- I2S/PCM data length, format, bit-clock polarity, PCM B mode, and PCM time-slot fields.
- DAC HPF, mute, zero-cross, auto-mute, and volume fields.
- ALC max/min gain, decay, attack, hold, target level, and enable.
- Clock detection power-up, sample-rate range, alternate sample-rate, and divider max fields.
- Analog enable masks for VMID, bias, DACs, DAC clocks, Class-D, and power-down bits.
- Clip and DAC reference fields.

Important exported-to-C-file declarations:

- `NAU8325_CODEC_DAI`, the DAI name `nau8325-hifi`.
- `struct nau8325`, the driver runtime state.
- `struct nau8325_src_attr`, divider/multiplier selector mapping.
- `enum NAU8325_MCLK_FS_RATIO_*`, indexes for 256/400/500 fs ratio choices.
- `struct nau8325_srate_attr`, per-sample-rate clock table entries.
- `struct nau8325_osr_attr`, DAC oversampling table entries.

## Control Flow and Behavioral Role

The header has no executable flow, but it drives the implementation:

1. Probe configures regmap with `NAU8325_REG_ADDR_LEN`, `NAU8325_REG_DATA_LEN`, and `NAU8325_REG_MAX`.
2. Reset helpers write hardware and software reset registers.
3. Init code writes ALC, clock detection, DAC reference, VMID, analog enable, Class-D, and oversampling fields using the masks defined here.
4. DAI `.set_sysclk`, `.startup`, and `.hw_params` use the clock, OSR, sample-rate, and I2S field definitions to derive valid playback configuration.
5. DAPM events use mute and clock-detection bits to avoid pops and control power-up policy.
6. ALSA controls use DAC volume, ALC, and oversampling masks to expose mixer settings.

## State and Persistence

`struct nau8325` persists runtime configuration and board policy: device, regmap, MCLK, sample rate, VREF impedance, DAC VREF voltage, clock-detection settings, and ALC enable. The header's register masks describe persistent hardware fields that survive until reset or explicit writes.

The regmap in the C file caches nonvolatile registers based on the address map here. If a register is incorrectly classified by the implementation's readable/writeable/volatile callbacks, state may be stale or inaccessible even though this header has a valid address.

## Dependencies and Integration Points

The header is included by `nau8325.c` and is private to the kernel driver. It assumes Linux integer types and bool are available through the including C file. Its constants integrate with:

- I2C regmap setup for 16-bit register and data width.
- ASoC DAI naming through `NAU8325_CODEC_DAI`.
- Firmware properties that fill `struct nau8325` board-policy fields.
- ALSA controls and DAPM events that use the masks to program the chip.

## Risks and Edge Cases

- `NAU8325_NAU8325_DAC_LEFT_MASK` appears to contain a duplicated prefix in the macro name. It may be harmless if unused, but it is an API cleanliness risk.
- `NAU8325_I2S_DF_RIGTH` appears misspelled. The C file uses the misspelled name, so renaming requires coordinated edits.
- `NAU8325_POWER_DOWN_R_MASK` shifts by `NAU8325_DACREFCAP_SFT` instead of `NAU8325_POWER_DOWN_R_SFT`, which looks like a probable mask bug. If used, it would target the wrong bits.
- Several fields define `_EN` names for masks rather than boolean values, for example volume masks. Callers must distinguish masks from values.
- The header exposes many analog and protection fields without value enums. Incorrect literal values in the implementation can still compile.
- `NAU8325_REG_MAX` is tied to `NAU8325_R73_RDAC`; new register additions must update both address definitions and regmap access callbacks.

## Test Signals

Useful validation signals include:

- Build tests for `nau8325.c` to catch misspelled macro dependencies.
- Static comparison of all masks against the datasheet, especially `POWER_DOWN_R_MASK`, I2S format names, clock masks, and analog enable masks.
- Regmap access tests ensuring every register used by the C file is readable/writeable/volatile as intended.
- Mixer-control tests for fields defined here: DAC volume, oversampling, and ALC controls.
- Clock and DAI format tests covering all field encodings used by `nau8325_hw_params()` and `nau8325_set_fmt()`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8325.h -->
