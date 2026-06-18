# Research Group subset-b-006460

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.c

## Purpose
`rt5659.c` is the Linux ASoC codec driver for Realtek RT5659/RT5658 devices on I2C. It binds the chip into ALSA SoC as a component with three digital audio interfaces, mixer controls, DAPM widgets/routes, clock and PLL programming, jack/button detection, GPIO/DMIC pin setup, runtime bias handling, suspend/resume register cache handling, and probe-time analog calibration. The driver is hardware-facing: most behavior is expressed as regmap writes/updates to the RT5659 register map defined in `rt5659.h`.

## Important APIs, Types, And Functions
- `rt5659_i2c_probe()` is the device entry point. It allocates `struct rt5659_priv`, copies platform data or parses device properties, enables optional GPIOs, initializes regmap, verifies `RT5659_DEVICE_ID == DEVICE_ID`, resets the codec, gets optional `mclk`, runs `rt5659_calibrate()`, applies board-specific input/DMIC/jack configuration, requests IRQ, and registers the ASoC component plus `rt5659_dai`.
- `soc_component_dev_rt5659` wires component callbacks: `probe`, `remove`, PM suspend/resume, `set_bias_level`, controls, DAPM widgets/routes, and component-level `set_sysclk`/`set_pll`.
- `rt5659_dai[]` exposes `rt5659-aif1`, `rt5659-aif2`, and `rt5659-aif3`, each with playback/capture, 8 kHz to 192 kHz rates, 8/16/20/24-bit formats, and `rt5659_aif_dai_ops`.
- DAI ops: `rt5659_hw_params()` programs sample width, pre-divider, and DAC OSR; `rt5659_set_dai_fmt()` programs master/slave, bitclock polarity, and I2S/left-justified/DSP formats; `rt5659_set_tdm_slot()` programs TDM enable, slot count, and slot width; `rt5659_set_bclk_ratio()` stores BCLK ratio and special-cases 64fs on AIF2/AIF3.
- Clock ops: `rt5659_set_component_sysclk()` selects MCLK, PLL1, or RCCLK and updates `rt5659->sysclk/sysclk_src`; `rt5659_set_component_pll()` selects PLL source from MCLK or BCLK1-3, uses `rl6231_pll_calc()`, writes PLL M/N/K registers, and stores PLL state.
- Jack APIs: exported `rt5659_set_jack_detect()` attaches an ALSA jack and queues detection work; `rt5659_irq()` schedules delayed work; `rt5659_jack_detect_work()` handles headset/headphone/button reports; `rt5659_jack_detect_intel_hd_header()` handles split HP/mic status for Intel HD Audio header mode.
- DAPM helpers such as `set_dmic_clk()`, `set_adc1_clk()`, `set_adc2_clk()`, `is_sys_clk_from_pll()`, `is_using_asrc()`, `rt5659_spk_event()`, `rt5659_mono_event()`, `rt5659_hp_event()`, and `rt5659_charge_pump_event()` attach register side effects to power graph transitions.
- Register access metadata is provided by `rt5659_reg[]`, `rt5659_volatile_register()`, `rt5659_readable_register()`, and `rt5659_regmap`.

## Control Flow
Probe begins with board data ingestion from platform data or device properties: `realtek,in1-differential`, `realtek,in3-differential`, `realtek,in4-differential`, `realtek,dmic1-data-pin`, `realtek,dmic2-data-pin`, and `realtek,jd-src`. Optional `ldo1-en` and `reset` GPIOs are requested high, then the driver waits 300 ms before creating a 16-bit register/16-bit value regmap. After device ID validation and reset, optional MCLK is fetched and `rt5659_calibrate()` performs a long sequence for headphone, speaker, and mono calibration, including polling completion bits with timeout counters.

After calibration, probe applies static board choices. Differential input flags set bits in `RT5659_IN1_IN2` and `RT5659_IN3_IN4`. DMIC platform data selects GPIO and DMIC data path bits; when no DMIC pin is configured, affected GPIOs are returned to GPIO mode and DMIC data path defaults to IN2N/IN2P. Jack-detect mode then determines the work handler and initial register setup: `RT5659_JD3` configures embedded jack detection and normal headset work; `RT5659_JD_HDA_HEADER` configures GPIO/IRQ/mic-detect behavior and calls the HDA-header setup routine. If an I2C IRQ exists, it is requested as a threaded rising/falling one-shot IRQ and GPIO1 is muxed as IRQ output. Finally `devm_snd_soc_register_component()` publishes the codec.

During PCM startup, machine drivers call DAI/component clock setup and `hw_params`. `hw_params` derives the codec pre-divider from current `sysclk` and sample rate through `rl6231_get_clk_info()`, rejects invalid frame sizes and widths, writes the data length into the selected I2S SDP register, writes the pre-divider in `RT5659_ADDA_CLK_1`, and sets DAC OSR based on 192 kHz, 96 kHz, or lower rates. `set_fmt` maps ASoC format flags into register fields. `set_tdm_slot` validates slots of 2/4/6/8 and widths of 16/20/24/32, then updates `RT5659_TDM_CTRL_1`.

DAPM controls most audio routing and power transitions. The driver declares user controls, source enums, mixers, muxes, supplies, ADCs/DACs, AIF endpoints, and output endpoints, then links them with a large route table. Conditional routes enable PLL supply only when global clock selects PLL and ASRC supplies only when ASRC tracking fields indicate an active target. Event handlers program depop, charge pump, class-D, mono amp, headphone, ADC chopper clocks, and DMIC clock settings around power-up/power-down.

Jack detection is interrupt-driven but debounced via delayed work. Normal mode reads `RT5659_INT_ST_1`; on insertion it calls `rt5659_headset_detect()` to power mic-detect, toggle embedded detection, poll `RT5659_EJD_CTRL_2`, and classify headset versus headphone. Headsets enable four-button inline IRQ support and force MICBIAS/mic-detect DAPM pins. Subsequent interrupts while inserted read `RT5659_4BTN_IL_CMD_1` and map button code groups to `SND_JACK_BTN_0..3`; releases or unknown codes report only the current jack type. Removal disables mic-detect and button IRQ as needed. HDA-header mode separately tracks headphone GPIO state and inline-mic state, updating `jack_type` with `SND_JACK_HEADPHONE` and `SND_JACK_MICROPHONE`.

## State And Persistence
Persistent driver state is in `struct rt5659_priv`: `component`, `regmap`, platform data, optional GPIO descriptors, ALSA jack pointer, delayed work, optional `mclk`, per-AIF `lrck`, `bclk`, and `master` arrays, PLL and sysclk selections/frequencies, current `jack_type`, and HDA-header HP/mic booleans. Hardware state persists in codec registers and is cached by regmap using `REGCACHE_RBTREE`. Suspend sets cache-only mode and marks the cache dirty; resume disables cache-only mode and syncs the cache back to hardware. Remove/shutdown write reset to the codec.

Bias transitions are stateful. `SND_SOC_BIAS_PREPARE` enables digital gate, LDO, micbias/VREF rails, waits, then enables fast VREF bits. `SND_SOC_BIAS_STANDBY` enables `mclk` when leaving off. `SND_SOC_BIAS_OFF` powers down LDO/VREF/gate and disables `mclk`. Jack detection also temporarily forces DAPM pins and can leave button-detect power enabled while a headset remains inserted.

## Dependencies And Integration Points
This driver depends on Linux I2C, regmap, common clock, GPIO descriptor, ACPI/OF device matching, ALSA SoC component/DAI/DAPM/control APIs, ALSA jack reporting, and Realtek helper functions from `rl6231.h`. It includes public platform data from `<sound/rt5659.h>` and private register definitions from `rt5659.h`. Board integration occurs through I2C IDs `rt5658`/`rt5659`, OF compatibles `realtek,rt5658`/`realtek,rt5659`, ACPI IDs `10EC5658`/`10EC5659`, optional `mclk`, optional GPIOs named `ldo1-en` and `reset`, optional I2C IRQ, and Realtek-specific device properties.

The ASoC machine driver integrates by selecting DAI links to `rt5659-aif1/2/3`, calling sysclk/PLL/format/slot APIs, and optionally calling exported `rt5659_set_jack_detect()`. User space sees ALSA mixer controls such as speaker/headphone/line/mono output volumes, DAC/ADC volumes, capture switches, boost gains, and IF1 data switches. DAPM route names are part of machine-driver routing integration.

## Risks
- Probe-time calibration writes many magic values and contains sleeps/poll loops. Hardware variant differences, missing clocks, or reset/power sequencing changes can produce boot delays or failed calibration without much recovery.
- `rt5659_set_component_sysclk()` calls `clk_set_rate(rt5659->mclk, freq)` for MCLK without checking for a NULL optional clock, so machine drivers must avoid MCLK sysclk selection when no MCLK provider exists.
- Jack detection and button reporting rely on delayed work, cached `jack_type`, forced DAPM pins, and several register side effects. Race-prone areas include IRQ storms, removal during queued work, and transitions between headset button events and unplug events.
- `rt5659_button_detect()` clears/acknowledges by writing back the read value; incorrect assumptions about write-clear semantics could lose button events.
- The HDA-header path bypasses the normal DAPM `MICBIAS1`/`Mic Det Power` widget additions in component probe and directly manages related registers; behavior depends tightly on `jd_src`.
- The DAPM graph is large and uses many string names. Route or widget renames can silently break audio paths expected by board files.
- Power sequencing uses unconditional sleeps, including 450 ms DMIC power delay and calibration waits, which may affect resume/probe latency.
- Suspend/resume only uses regcache sync; GPIO reset or external power loss during suspend relies on platform data `power` behavior outside this file, except there is no explicit re-run of calibration on resume.

## Test Signals
- Build-test with `CONFIG_SND_SOC_RT5659`, OF, ACPI, GPIO, common clock, and PM combinations; verify no undefined register macros or callback signature drift.
- Probe on hardware should log successful ID read `0x6311`, complete calibration without "HP Calibration", "SPK Calibration", or "Mono Calibration" errors, and register all three DAIs.
- Audio playback/capture tests should cover AIF1/AIF2/AIF3, 8/16/20/24-bit formats, 8 kHz through 192 kHz rates, PLL and MCLK sysclk sources, TDM slot configurations, PDM/SPDIF outputs, analog inputs, DMIC inputs, speaker, headphone, line out, and mono output paths.
- Jack tests should cover `RT5659_JD3` headset/headphone insertion/removal, four-button press/release mapping, spurious interrupts, and `RT5659_JD_HDA_HEADER` separate HP/mic plug reporting.
- PM tests should suspend/resume during idle and active routes, verify regcache sync restores mixer/clock state, and verify MCLK enable/disable behavior across bias transitions.
- DAPM debugfs or ALSA route tracing should confirm conditional PLL/ASRC routes activate only when selected and that event handlers program depop/amp registers around power changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.h

## Purpose
`rt5659.h` is the private register and state definition header for the RT5659/RT5658 ASoC codec driver. It gives `rt5659.c` the symbolic register addresses, bit masks, shifts, enumerated clock/DAI identifiers, private state structure, and exported jack-detect prototype needed to program the codec. It complements the public `<sound/rt5659.h>` platform-data header and should be treated as tightly coupled to the driver's register writes, DAPM definitions, and regmap access lists.

## Important APIs, Types, And Definitions
- Register address macros define the codec's visible register map from `RT5659_RESET`, vendor/device IDs, output/input controls, ADC/DAC/mixer controls, PDM/SPDIF, power registers, I2S/TDM/DMIC/PLL/ASRC controls, jack/IRQ/GPIO controls, calibration/status registers, DRC/EQ/ALC blocks, and DAC/ADC EQ coefficient registers through `0x03f3`.
- Common masks and shifts define mute/volume fields, boost gains, mixer source bits, analog/digital power bits, I2S format fields, ADDA pre-divider/OSR fields, DMIC data-path fields, PLL fields, ASRC fields, depop/charge-pump fields, micbias fields, IRQ/jack fields, GPIO pin muxes, noise-gate bits, and class-D/chopper bits.
- `DEVICE_ID` is `0x6311`, the value validated by `rt5659_i2c_probe()`.
- Clock enums define system clock sources `RT5659_SCLK_S_MCLK`, `RT5659_SCLK_S_PLL1`, and `RT5659_SCLK_S_RCCLK`; PLL source enums cover MCLK and BCLK1-BCLK4; DAI enums define `RT5659_AIF1` through `RT5659_AIF4` and `RT5659_AIFS`.
- `struct rt5659_pll_code` mirrors M/N/K PLL fields but the C file actually uses `struct rl6231_pll_code` for calculation.
- `struct rt5659_priv` is the driver's main persistent state: component, public platform data, regmap, optional GPIOs, jack pointer, delayed work, MCLK, sysclk source/frequency, per-AIF LRCK/BCLK/master arrays, vendor ID, PLL source/input/output, current jack type, and HDA-header HP/mic booleans.
- `rt5659_set_jack_detect()` is declared for machine drivers and exported by `rt5659.c`.

## Control Flow Role
The header has no executable control flow, but it determines almost every branch and register update in `rt5659.c`. Probe uses register IDs, device ID, GPIO/DMIC mux masks, differential-input masks, jack-detect constants, and power bits. PCM setup uses I2S data format masks, pre-divider fields, DAC OSR fields, TDM data fields, and clock-source enums. PLL setup uses PLL source, M/N/K, and global-clock masks. DAPM uses power-bit constants, mixer source/mute bits, ASRC fields, depop/charge-pump bits, class-D bits, and ADC/DAC chopper bits. Jack handling uses IRQ, inline-button, mic-detect, EJD/JD, GPIO status, and micbias/power constants.

Because the macros are direct numeric encodings of hardware fields, changes in this header immediately alter hardware programming. The header also fixes array sizing through `RT5659_AIFS`; `rt5659_priv.lrck`, `bclk`, and `master` arrays are indexed by DAI IDs declared here.

## State And Persistence
State is declared but not persisted in this header. `struct rt5659_priv` instances are allocated per I2C device by `rt5659_i2c_probe()` and live until device removal. Register state persists in hardware and regcache. The fields in `rt5659_priv` mirror selected hardware state that the driver needs to avoid redundant clock/PLL programming (`sysclk`, `sysclk_src`, `pll_src`, `pll_in`, `pll_out`), configure PCM operations per AIF (`lrck`, `bclk`, `master`), and report jack status (`jack_type`, `hda_hp_plugged`, `hda_mic_plugged`).

## Dependencies And Integration Points
The header includes `<sound/rt5659.h>` for public platform data and jack/DMIC constants such as `struct rt5659_platform_data`, `RT5659_DMIC1_*`, `RT5659_DMIC2_*`, and jack-source values used by the C file. It is included only by the private driver implementation and indirectly depends on ALSA SoC types, regmap, GPIO descriptors, clock, and workqueue types through `struct rt5659_priv` fields as seen from `rt5659.c`.

The macro names are part of the internal integration contract between regmap defaults/readability lists, ALSA controls, DAPM widgets/routes, DAI ops, calibration sequences, and device-property handling. They also make device-tree/platform-data values meaningful by mapping board choices to hardware pin muxes and input modes.

## Risks
- The file is very large and mostly manually transcribed hardware constants. A single wrong mask, shift, or address can affect unrelated audio paths or power domains.
- Some names contain historical typos such as `CAILB`, and callers must use the exact macro names. Renaming for cleanup would be high churn and easy to miss.
- `RT5659_AM_DIS` is defined with the same value as `RT5659_AM_EN`, which may be intentional hardware semantics or a latent typo; any code using it should be checked carefully.
- `struct rt5659_pll_code` appears unused in the driver because `rl6231_pll_code` is used instead; this can mislead maintainers or become stale.
- DAI enum sizing includes `RT5659_AIF4` even though `rt5659.c` registers only AIF1-AIF3. Array bounds are safe for current IDs, but new DAI additions must keep the enum, arrays, and DAI table aligned.
- The private header and C file must evolve together. Adding a register to DAPM or controls without adding it to readable/volatile/default lists in `rt5659.c` can create regmap cache/debug surprises.

## Test Signals
- Compile `rt5659.c` with this header and all supported Kconfig combinations to catch missing or incompatible macros.
- Runtime probe should validate `DEVICE_ID` and access all registers listed in the C file's regmap default/readable/volatile tables without regmap errors.
- ALSA control smoke tests should exercise volume/mute/boost controls that use the global field macros and mixer field macros.
- DAI tests should verify I2S data length/format, ADDA pre-divider, BCLK ratio, PLL source, and TDM slot programming reflected by the corresponding register bit fields.
- Board tests should verify DMIC pin mux selections, jack source modes, GPIO IRQ pin muxing, differential input configuration, and ASRC/PLL conditional DAPM routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5659.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5660.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5660.c

## Purpose
`rt5660.c` is the Linux ASoC codec driver for the Realtek RT5660 I2C audio codec. Compared with `rt5659.c`, it is a smaller single-AIF codec driver: it registers one playback/capture DAI, defines ALSA mixer controls, models analog/digital routing through DAPM, programs sysclk/PLL/I2S parameters, applies a small regmap patch including private-register access, handles bias and PM regcache transitions, and applies board-specific differential input and DMIC pin configuration.

## Important APIs, Types, And Functions
- `rt5660_i2c_probe()` allocates `struct rt5660_priv`, obtains optional `mclk`, loads platform data or DT properties, initializes regmap, validates `RT5660_VENDOR_ID2 == RT5660_DEVICE_ID`, resets the codec, applies `rt5660_patch`, enables automatic amp disable/MCLK detect/clock detect, configures optional DMIC pins, and registers the component plus `rt5660_dai`.
- `rt5660_ranges[]` maps a virtual private-register range beginning at `RT5660_PR_BASE` through `RT5660_PRIV_INDEX`/`RT5660_PRIV_DATA`; `rt5660_patch[]` writes `RT5660_ALC_PGA_CTRL2` and private register `0x3d`.
- `rt5660_reg[]`, `rt5660_volatile_register()`, `rt5660_readable_register()`, and `rt5660_regmap` define an 8-bit register/16-bit value regmap with private range support, single reads/writes, and `REGCACHE_MAPLE`.
- `rt5660_snd_controls[]` exposes speaker, output, DAC, input boost, ADC capture, and ADC boost controls with TLV scales.
- `rt5660_dapm_widgets[]` and `rt5660_dapm_routes[]` describe MICBIAS, DMIC, input boosters, record mixers, ADCs, IF1, DAC mixers, speaker/output/LOUT paths, PLL-gated filters, and output endpoints.
- DAI ops include `rt5660_hw_params()`, `rt5660_set_dai_fmt()`, `rt5660_set_dai_sysclk()`, and `rt5660_set_dai_pll()`.
- PM/component callbacks include `rt5660_set_bias_level()`, `rt5660_probe()`, `rt5660_remove()`, `rt5660_suspend()`, and `rt5660_resume()`.

## Control Flow
I2C probe begins by allocating private state and fetching optional `mclk`. Platform data wins; otherwise device-tree properties are parsed only when `of_node` exists. `rt5660_parse_dt()` reads `realtek,in1-differential`, `realtek,in3-differential`, `realtek,poweroff-in-suspend`, and `realtek,dmic1-data-pin`. After regmap setup, the driver reads `RT5660_VENDOR_ID2`, checks for `0x6338`, resets the chip, applies the register patch, and enables clock/amp helper bits in `RT5660_GEN_CTRL1`. If DMIC1 is configured, GPIO1 becomes DMIC SCL and either GPIO2 or IN1P is selected as DMIC data. The component registration publishes the controls, DAPM graph, and `rt5660-aif1`.

During PCM `hw_params`, the driver stores `lrck[dai->id]`, calculates the ADDA pre-divider from `sysclk` and LRCK through `rl6231_get_clk_info()`, validates the frame size, derives BCLK as LRCK times 32 or 64 depending on frame size, maps sample width into `RT5660_I2S_DL_*`, and for AIF1 writes `RT5660_I2S1_SDP` and `RT5660_ADDA_CLK1`. Unsupported DAI IDs, widths, sample/clock relationships, and negative frame sizes are rejected.

`rt5660_set_dai_fmt()` maps ASoC master/slave, inversion, and serial format flags into `RT5660_I2S1_SDP`. Only normal bitclock/frame polarity and inverted bitclock/non-inverted frame are supported; I2S, left-justified, DSP_A, and DSP_B are supported. `rt5660_set_dai_sysclk()` records and writes MCLK, PLL1, or RCCLK as the system clock source. `rt5660_set_dai_pll()` selects PLL source from MCLK or BCLK, computes PLL M/N/K via `rl6231_pll_calc()`, writes PLL control registers, and caches PLL input/output/source; zero input or output disables PLL by selecting MCLK.

DAPM controls audio flow. Capture can route analog inputs through boosters and record mixers or DMIC through DMIC clock/power into stereo ADC mixers, then through IF1 ADC swap mux to `AIF1TX`. Playback routes `AIF1RX` through IF1 DAC swap mux, DAC1 mixers, stereo DAC mixers, DACs, output mixers, and then speaker or line-out paths. PLL1 is included as a conditional supply for ADC/DAC filters only when global clock selects PLL. `rt5660_lout_event()` programs LOUT amp output clamp/bias bits on power transitions, and `rt5660_set_dmic_clk()` calculates a DMIC clock divider from sysclk and I2S pre-divider.

Bias and PM flow are split. `SND_SOC_BIAS_PREPARE` enables digital gate and toggles `mclk`: if transitioning from ON it disables `mclk`, otherwise it prepares/enables it. `SND_SOC_BIAS_STANDBY` coming from OFF powers VREF, micbias, bandgap, waits, and enables fast VREF bits. `SND_SOC_BIAS_OFF` clears digital gate. Suspend sets regcache cache-only and dirty; resume optionally sleeps 350 ms when `poweroff_codec_in_suspend` is set, then syncs regcache.

## State And Persistence
Runtime state lives in `struct rt5660_priv` from `rt5660.h`: component, platform data, regmap, MCLK, sysclk source/frequency, per-DAI LRCK/BCLK/master arrays, and PLL source/input/output. Hardware register state is cached by regmap. Private registers are accessed through regmap's range mapping, so writes to `RT5660_PR_BASE + offset` are persisted through the selector/window mechanism and participate in regmap semantics.

The driver stores enough state to suppress redundant sysclk/PLL programming and to derive DMIC and BCLK settings during DAPM/PCM operations. Suspend/resume persistence depends on regcache sync; optional board-level codec power-off during suspend is represented only by a resume delay before sync, not by recalibration.

## Dependencies And Integration Points
The driver depends on Linux I2C, regmap range mapping, common clock, ACPI/OF matching, PM, ALSA SoC component/DAI/DAPM/control APIs, TLV helpers, and Realtek `rl6231` clock/PLL helpers. It includes private definitions from `rt5660.h`. It binds I2C ID `rt5660`, OF compatible `realtek,rt5660`, and ACPI IDs `10EC3277`/`10EC5660`.

Machine drivers integrate through `rt5660-aif1`, DAI clock/format/PLL callbacks, DAPM route names, and board data/device properties for differential inputs, power-off-in-suspend, and DMIC1 data pin. User-space integration is through ALSA controls for speaker/output volumes and switches, DAC volume, input boosts, ADC capture switch/volume, and ADC boost gain.

## Risks
- `rt5660_parse_dt()` captures `in1_diff` and `in3_diff`, but `rt5660_i2c_probe()` does not appear to apply these fields to input registers in this file. If not handled elsewhere, differential input properties may be parsed but ineffective.
- The optional MCLK can be absent, yet bias handling calls `clk_prepare_enable()`/`clk_disable_unprepare()` on `rt5660->mclk`; this relies on common clock optional semantics being safe for NULL or on machine setup avoiding paths that require MCLK.
- Private-register range mapping is central to the patch and ADC clock DAPM supply. Incorrect range settings can write the wrong private register through `RT5660_PRIV_INDEX`/`RT5660_PRIV_DATA`.
- PM resume after board-level poweroff only delays and syncs regcache; if hardware loses state that is not in regcache or requires analog sequencing, resume may be incomplete.
- The driver supports only AIF1. DAI op code rejects other DAI IDs, so board files must not assume multi-interface behavior like related Realtek codecs.
- Clock setup depends on machine drivers setting `sysclk` before `hw_params`; otherwise pre-divider calculation can fail or compute from zero.
- DAPM route names and mixer bit definitions must stay synchronized with `rt5660.h`; route string changes can break board-level routing.

## Test Signals
- Build with `CONFIG_SND_SOC_RT5660`, OF, ACPI, PM, and regmap enabled; ensure private range, maple cache, and DAI callbacks compile against current kernel APIs.
- Probe on target hardware should read vendor/device ID `0x6338`, reset successfully, apply `rt5660_patch` without warnings, and register `rt5660-aif1`.
- PCM tests should cover 8 kHz to 192 kHz rates, 8/16/20/24-bit formats, frame sizes requiring 32fs and 64fs BCLK, MCLK/PLL/RCCLK system clock selection, and PLL from MCLK/BCLK.
- Capture tests should verify analog BST1/BST2/BST3 paths and DMIC1 paths for GPIO2 and IN1P data selections. Differential input property behavior should be specifically checked because the parsed fields are not visibly applied.
- Playback tests should cover DAC-to-speaker and DAC/output-to-LOUT paths, LOUT power event side effects, mixer switches, and volume controls.
- PM tests should suspend/resume with and without `realtek,poweroff-in-suspend`, then verify regcache restoration and audio path recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5660.c -->
