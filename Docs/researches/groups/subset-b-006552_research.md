# subset-b-006552 research

Grouped research for Tegra and Allwinner ASoC source files. Each section title preserves the source path and is wrapped for reconciliation into the requested per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-dmic.c

## Purpose
This is the platform ASoC CPU-DAI driver for the Allwinner H6 `sun50i` digital microphone controller. It exposes a capture-only DAI named `dmic`, programs the DMIC sample rate/channel/FIFO registers, registers DMA engine PCM support, and manages the controller's bus/module clocks and optional reset line through runtime PM.

## Important APIs, types, and functions
The central state is `struct sun50i_dmic_dev`, which holds the `dmic_clk`, `bus_clk`, optional reset, MMIO regmap, and RX DMA descriptor. `dmic_rate_s` maps ALSA rates to the controller's sample-rate field. The ASoC operations are `sun50i_dmic_startup()`, `sun50i_dmic_hw_params()`, `sun50i_dmic_trigger()`, and `sun50i_dmic_soc_dai_probe()`. `sun50i_dmic_probe()` maps registers, creates a 32-bit uncached MMIO regmap, acquires clocks, initializes DMA parameters at `SUN50I_DMIC_DATA`, deasserts reset, registers the component/DAI, enables runtime PM, and registers DMAengine PCM. Mixer controls expose four stereo channel volume controls using `SOC_DOUBLE_TLV`.

## Control flow
Probe allocates state, maps resources, initializes regmap and clocks, sets `dma_params_rx.addr` and `maxburst`, deasserts reset, registers the component, enables PM, and registers DMAengine PCM. On stream startup, non-capture streams are rejected, RX FIFO is flushed, and the counter register is reset. `hw_params()` programs channel count, HPF enable mask, channel enable mask, FIFO sample size and MSB mode, module-clock rate (`22.5792 MHz` for 44.1 kHz family, `24.576 MHz` for 48 kHz family), the hardware rate selector, DMA bus width, and oversampling mode. `trigger()` enables/disables DMA request generation and global DMIC enable for START/STOP-style commands.

## State and persistence
Hardware state lives in DMIC registers and is not cached (`REGCACHE_NONE`). Runtime suspend disables both clocks; runtime resume prepares the module and bus clocks. There is no explicit reprogramming after suspend beyond normal stream setup, so correctness depends on stream lifecycle and PM not losing configured registers while active. The DMA address width is mutable per `hw_params()`.

## Dependencies and integration points
The driver integrates with platform DT matching for `allwinner,sun50i-h6-dmic`, Linux clocks named `bus` and `mod`, optional reset controller, regmap MMIO, ASoC component/DAI registration, and `snd_dmaengine_pcm`. It exports capture formats `S16_LE` and `S24_LE`, rates from 8 kHz to 48 kHz, and up to 8 channels.

## Risks and edge cases
Unsupported playback, rates outside the hardcoded table, sample formats other than 16/24-bit, or physical widths other than 16/32 bits are rejected. `chan_en = (1 << channels) - 1` assumes validated channel counts. Clock rate failures become `-EINVAL`, losing the lower-level error code. Runtime PM has no register cache, so suspend during configured-but-inactive periods could require subsequent full stream setup. The code exposes only four stereo volume controls although capture supports eight channels.

## Test signals
Useful checks include DT probe with required clocks, capture open rejecting playback, 8/44.1/48 kHz families selecting the expected module clock and rate bits, S16/S24 DMA width selection, trigger toggling DRQ/global enable, runtime suspend/resume clock balancing, and DMA capture smoke tests at 1, 2, and 8 channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.c

## Purpose
This helper exposes the Allwinner ADDA analog codec PRCM access register as a normal Linux regmap. The analog codec controls are not directly memory-mapped; reads and writes are tunneled through address, data-in, data-out, reset, and write-strobe fields in one 32-bit `ADDA_PR` register.

## Important APIs, types, and functions
`adda_reg_read()` and `adda_reg_write()` implement regmap bus callbacks over `readl()`/`writel()`. `adda_pr_regmap_cfg` defines 5-bit register addresses, 8-bit values, stride 1, `fast_io`, and `max_register = 31`. `sun8i_adda_pr_regmap_init()` is the exported API used by the analog codec driver to create a devm-managed regmap with the MMIO base as callback context.

## Control flow
Reads deassert ADDA reset, clear write mode, program the 5-bit analog register address into `ADDA_PR_ADDR`, then return the low 8-bit data-out field. Writes deassert reset, program the address, program the 8-bit data-in field, pulse `ADDA_PR_WRITE`, and clear the write bit. Initialization is a thin wrapper around `devm_regmap_init()`.

## State and persistence
The shim has no private state beyond the MMIO base pointer passed as regmap context. It does not use a software cache and relies on the consumer regmap/device lifecycle. Every access deasserts the analog reset bit, so access itself can bring the analog register bridge out of reset.

## Dependencies and integration points
It depends on MMIO accessors, regmap callback mode, and the declaration in `sun8i-adda-pr-regmap.h`. `sun8i-codec-analog.c` consumes this helper to register ASoC controls for the analog codec block. The symbol is exported GPL for other in-tree Allwinner analog codec users.

## Risks and edge cases
The read/write helpers perform read-modify-write sequences without explicit locking beyond whatever regmap serializes, so direct external access to the same PRCM register would be unsafe. There is no timeout or posted-write readback around the write strobe. Address and data are masked down to hardware width, so out-of-range values are silently truncated by the callback path after regmap's register limit checks.

## Test signals
Probe an analog codec user and verify regmap debugfs shows 5-bit registers. Exercise ALSA controls that span multiple analog registers, confirm writes pulse `ADDA_PR_WRITE`, and test suspend/resume or reset scenarios where each access must deassert `ADDA_PR_RESET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.h -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.h

## Purpose
This header declares the ADDA PR regmap factory used to access Allwinner analog audio codec registers through a PRCM bridge register.

## Important APIs, types, and functions
The single API is `struct regmap *sun8i_adda_pr_regmap_init(struct device *dev, void __iomem *base);`. It returns a devm-managed regmap or an error pointer. The declaration assumes users include appropriate kernel declarations for `struct device`, `void __iomem`, and `struct regmap` through their source includes.

## Control flow
There is no executable control flow in the header. Consumers call the initializer after mapping the PRCM/analog register resource and pass the mapped base address into the helper.

## State and persistence
The header owns no state. Persistence semantics are defined by the implementation's regmap and the consumer driver's device-managed lifetime.

## Dependencies and integration points
`sun8i-codec-analog.c` includes this header and calls the initializer during platform probe. The declaration is paired with the GPL-exported implementation in `sun8i-adda-pr-regmap.c`.

## Risks and edge cases
The header has no include guard and no forward declarations, so it relies on current include order. Multiple inclusion is currently harmless because it only contains one compatible function declaration, but adding types or inline helpers later would require a guard.

## Test signals
Compile coverage is the primary signal: any missing declaration, include-order problem, or signature drift between the header and implementation will fail builds of analog codec users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec-analog.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec-analog.c

## Purpose
This ASoC component driver models the analog half of several Allwinner internal codecs. It provides mixer, amplifier, bias, headphone, line-in, line-out, and microphone DAPM widgets and controls for A23, H3, and V3s-style analog blocks. It complements the separate digital codec driver, which supplies stream-facing DAI widgets.

## Important APIs, types, and functions
The file defines analog register offsets and bit fields for HP volume, mixers, DAC/PA source control, line/mic gains, bias, ADC enable, and output enables. Feature-specific helper functions add controls/widgets/routes: `sun8i_codec_add_headphone()`, `sun8i_codec_add_mbias()`, `sun8i_codec_add_hmic()`, `sun8i_codec_add_linein()`, `sun8i_codec_add_lineout()`, and `sun8i_codec_add_mic2()`. `struct sun8i_codec_analog_quirks` selects which blocks exist per compatible. `sun8i_codec_analog_cmpnt_probe()` builds the component's dynamic DAPM topology based on quirks. `sun8i_codec_analog_probe()` maps MMIO, creates the ADDA PR regmap, and registers the component.

## Control flow
Component registration installs common Mic1/ADC/DAC controls and widgets. At component probe, the driver obtains match data, adds a generic mixer topology or a V3s-limited topology when neither MIC2 nor line-in exists, then conditionally adds headphone, HMIC bias, line-in, line-out, MBIAS, and MIC2 blocks. Headphone amplifier power-up is intercepted by `sun8i_headphone_amp_event()`, which enables the PA and sleeps 700 ms before completion; power-down clears the PA enable bit.

## State and persistence
The driver has no long-lived private state beyond the regmap registered with the component. Hardware state is DAPM-managed through analog registers behind the ADDA PR regmap. ALSA control state persists in hardware/register cache according to regmap/component behavior. The headphone event intentionally serializes a long analog settling delay into DAPM power sequencing.

## Dependencies and integration points
It depends on `sun8i_adda_pr_regmap_init()`, ASoC DAPM, TLV controls, and DT compatibles `allwinner,sun8i-a23-codec-analog`, `allwinner,sun8i-h3-codec-analog`, and `allwinner,sun8i-v3s-codec-analog`. The analog widgets are intended to be linked at card level to stream widgets from the digital codec because the analog and digital blocks are separate ASoC components.

## Risks and edge cases
Dynamic topology must match SoC capabilities exactly; a missing quirk can expose controls for nonexistent pins or omit needed routes. The H3 line-out enable reuses a bit named for headphone PA on other SoCs, so register semantics are compatible only under the selected quirk. The V3s mixer special case is explicitly incomplete for all possible feature combinations. The 700 ms headphone delay can be user-visible and can affect power event latency. `of_device_get_match_data()` is assumed non-null for DT-created devices.

## Test signals
Validate each compatible's ALSA mixer list and DAPM graph. Exercise headphone, line-in/out, MIC1/MIC2, HBIAS/MBIAS routes, and ADC/DAC paths with `dapm_pop_time`/debugfs route inspection. Confirm no controls reference absent feature bits on V3s and that headphone pop suppression timing works on A23-style hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec.c

## Purpose
This is the digital ASoC codec driver for Allwinner A33/A64 internal codecs. It exposes three DAIs (`AIF1`, `AIF2`, `AIF3`), digital mixer/mux topology, DAC/ADC power widgets, sample clock programming, runtime PM, optional legacy DAPM names for old device trees, and A64 headset/button jack detection.

## Important APIs, types, and functions
`struct sun8i_codec` stores regmap, clocks, quirk data, per-AIF state, jack state, delayed work, IRQ state, and protected sysclk metadata. `struct sun8i_codec_aif` tracks LRCK divider, sample rate, slot geometry, active streams, and open streams. DAI operations include `sun8i_codec_set_fmt()`, `sun8i_codec_set_tdm_slot()`, `sun8i_codec_startup()`, `sun8i_codec_hw_params()`, and `sun8i_codec_hw_free()`. Clock helpers include `sun8i_codec_get_hw_rate()`, `sun8i_codec_update_sample_rate()`, `sun8i_codec_get_bclk_div()`, `sun8i_codec_get_lrck_div_order()`, and `sun8i_codec_get_sysclk_rate()`. Jack detection is handled by `sun8i_codec_enable_jack_detect()`, `sun8i_codec_jack_irq()`, and `sun8i_codec_jack_work()`.

## Control flow
Probe allocates state, reads quirks, initializes delayed work and mutex, gets clocks, maps registers, creates a cached MMIO regmap, enables runtime PM, and registers the component and three DAIs. Component probe optionally adds legacy widgets, chooses PLL_AUDIO as AIF clock source, selects AIF1CLK as SYSCLK source, and programs a default passthrough sample rate. Stream startup constrains AIF1 rates based on any protected module-clock rate. `hw_params()` programs word size, LRCK and BCLK dividers, enforces shared AIF2/AIF3 clock compatibility, sets or protects the module clock, records per-AIF open state, and updates the system sample-rate register to the highest active rate. `hw_free()` releases exclusive clock protection when the last stream on an AIF closes. DAPM AIF events update active stream bits and recompute sample rate.

## State and persistence
Register state is cached with `REGCACHE_FLAT`; runtime suspend switches to cache-only, marks dirty, and disables the bus clock, while resume reenables the bus clock and syncs cached state. The module clock rate is protected with `clk_set_rate_exclusive()` and `clk_rate_exclusive_put()` across open AIFs. Jack state persists in `jack_status`, `last_hmic_irq`, `jack_last_sample`, and `jack_hbias_ready`, protected by `jack_mutex` and a delayed work item.

## Dependencies and integration points
The driver integrates with DT compatibles `allwinner,sun8i-a33-codec` and `allwinner,sun50i-a64-codec`, ASoC DAI/component/DAPM APIs, runtime PM, clocks named `bus` and `mod`, IRQ resources for HMIC on A64, and the card-level DAPM links to the analog codec component. It exposes broad PCM format/rate support including 7.35/14.7/29.4 kHz and high rates up to 192 kHz.

## Risks and edge cases
The shared module clock creates conflicts when streams require different 22.5792/24.576 MHz families; these are detected via constraints and exclusive clock rate errors. AIF2 and AIF3 share BCLK/LRCK generation, so simultaneous use must match sample and bit rates. AIF3 supports only master DSP mode. DAPM route names must align with machine-card routes to the analog codec. Jack detection uses delayed HBIAS stabilization and ADC thresholds; spurious in/out ordering, IRQ storms, or missing HBIAS route can cause misreports. The quirk-driven LRCK inversion means format regressions may be board-specific.

## Test signals
Run playback/capture on AIF1/AIF2/AIF3, simultaneous AIF2+AIF3 with matching and mismatched parameters, 44.1 kHz and 48 kHz family streams, TDM slot override cases, runtime PM suspend/resume with cached controls, old DT legacy routes, and A64 headset plug/unplug plus button ADC thresholds. Inspect DAPM debugfs to confirm digital-to-analog route stitching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/Kconfig

## Purpose
This Kconfig menu defines build-time selection for NVIDIA Tegra ASoC platform, component, and machine drivers. It gates common Tegra audio support, individual controller blocks from Tegra20 through Tegra210/186, and board-level machine drivers for specific external codecs.

## Important APIs, types, and functions
The root symbol is `SND_SOC_TEGRA`, which depends on Tegra architecture or compile testing, common clock, and reset controller support, and selects `REGMAP_MMIO` plus generic DMAengine PCM support. Subsymbols include Tegra20 AC97/DAS/I2S/SPDIF, Tegra30 AHUB/I2S, Tegra210 AHUB/DMIC/I2S/OPE/ADMAIF/MVC/SFC/AMX/ADX/MIXER, Tegra186 ASRC/DSPK, generic audio graph card support, a hidden `SND_SOC_TEGRA_MACHINE_DRV`, and multiple codec-specific machine drivers.

## Control flow
There is no runtime control flow. At configuration time, enabling `SND_SOC_TEGRA` exposes all nested symbols. Some controller symbols select required infrastructure, such as Tegra20 AC97/I2S selecting DAS. Machine-driver symbols select `SND_SOC_TEGRA_MACHINE_DRV` and the needed external codec drivers.

## State and persistence
Kconfig state persists in kernel configuration files. These selections determine which objects from the Tegra Makefile are compiled or built as modules.

## Dependencies and integration points
The file integrates with the kernel ASoC Kconfig tree, architecture symbols, common clock/reset subsystems, external codec symbols, I2C/GPIOLIB/INPUT/MFD dependencies, and the local Makefile's `obj-$(CONFIG_...)` rules.

## Risks and edge cases
Missing `select` dependencies cause link or runtime probe failures. Over-broad selects can force unwanted codec drivers. Some machine drivers depend on generic support and board-specific GPIO/I2C assumptions. `COMPILE_TEST` allows building outside Tegra, so source-level dependencies must remain architecture-neutral.

## Test signals
Run `olddefconfig`/`allyesconfig`/`allmodconfig` with Tegra and COMPILE_TEST, verify each selected symbol produces the expected module, and check that hidden machine support is pulled only by board drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/Makefile

## Purpose
This Makefile maps Tegra ASoC Kconfig symbols to kernel objects and compound modules. It is the build integration point for platform PCM, controller components, AHUB processing blocks, and machine/card drivers.

## Important APIs, types, and functions
Object definitions include `snd-soc-tegra-pcm-y := tegra_pcm.o`, per-controller one-object modules such as `snd-soc-tegra20-i2s-y := tegra20_i2s.o`, compound modules such as `snd-soc-tegra210-admaif-y := tegra210_admaif.o tegra_isomgr_bw.o`, and OPE composed from OPE/MBDRC/PEQ files. `obj-$(CONFIG_...)` lines bind each module to its Kconfig symbol.

## Control flow
There is no runtime flow. Kbuild expands `obj-*` rules based on `.config`, compiles listed source objects, and links them into modules or built-in objects named by the left-hand module variables.

## State and persistence
The Makefile has no runtime state; it persists the build topology. Module names are ABI-visible to packaging, initramfs, and modprobe users.

## Dependencies and integration points
It integrates directly with `sound/soc/tegra/Kconfig`, Kbuild, and all local Tegra source files. The machine support section builds WM8903, WM8962, common machine support, and audio graph card objects.

## Risks and edge cases
If Kconfig and Makefile symbols drift, enabled drivers silently do not build or objects build under the wrong name. Compound module definitions must include all helper objects needed at link time. Renaming a source file requires updating both the module variable and `obj-*` mapping.

## Test signals
Build with each relevant `CONFIG_SND_SOC_TEGRA*` as `m` and `y`, inspect resulting module names, and run `modpost`/link checks for missing helper objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.c

## Purpose
This ASoC component driver controls the Tegra186/Tegra264 asynchronous sample-rate converter. It exposes CIF DAIs for ASRC RX/TX paths, DAPM routes through the Tegra audio crossbar, user controls for sample-rate ratio source/value and thresholds, and runtime PM state restoration for conversion lanes.

## Important APIs, types, and functions
`tegra186_asrc_reg_defaults` seeds per-stream and global registers. `tegra186_asrc_set_audio_cif()` translates PCM params into Tegra CIF configuration. `tegra186_asrc_in_hw_params()` programs RX thresholds and RX CIF, while `tegra186_asrc_out_hw_params()` programs TX thresholds/CIF, HW ratio compensation, ratio source, software ratio registers, and lock status. Getter/setter controls manipulate `asrc->lane[]` fields and sometimes hardware registers. `tegra186_asrc_widget_event()` soft-resets a stream after DAPM power-down. Regmap callbacks define readable/writeable/volatile ranges across per-stream stride and global registers. Probe initializes regmap, SoC ARAM address data, defaults, DAIs, controls, routes, and PM.

## Control flow
Probe maps registers, creates cached MMIO regmap, selects Tegra186 or Tegra264 ARAM start address from DT match data, writes global 32-bit fractional precision while cache-only, initializes six lane state records, registers the component and DAIs, then enables runtime PM. Runtime resume leaves cache-only mode, writes scratch ARAM address and global enable before regcache sync, then replays software ratio registers and lock writes for lanes using SW ratio. Runtime suspend only marks the regcache dirty. During playback/capture setup, CIF formatting supports S16 and S24/S32, 1-12 channels, and fixed 24-bit client width. DAPM routes bind RXn CIF inputs to TXn CIF outputs for six streams and route RX7 to a depacketizer for ratio estimator input.

## State and persistence
Per-lane control state (`int_part`, `frac_part`, `ratio_source`, `hwcomp_disable`, `input_thresh`, `output_thresh`) is stored in `struct tegra186_asrc` and used to reprogram hardware on `hw_params()` and runtime resume. Regmap uses `REGCACHE_FLAT` with explicit volatile registers. Ratio integer/fraction registers are marked volatile, so software ratio state is replayed manually after PM.

## Dependencies and integration points
The driver depends on `tegra186_asrc.h`, Tegra CIF helper `tegra_set_cif()`, ASoC DAPM/control/DAI infrastructure, regmap MMIO, runtime PM, and DT compatibles `nvidia,tegra186-asrc` and `nvidia,tegra264-asrc`. DAI and route names are designed for Tegra AHUB/XBAR graph integration.

## Risks and edge cases
Software ratio writes are rejected while the lane source is ARAD, so userspace mixer ordering matters. Ratio lock sequencing is critical after any SW ratio change or PM resume. `Stream6 Input Threshold` is defined with `ASRC_STREAM_REG(..., 4)`, which appears to target stream 5's register rather than stream 6's index 5. DAI ID arithmetic assumes output DAIs start at ID 7. Missing error checks on `regcache_sync()` in runtime resume can hide restore failures. Volatile ratio registers require careful testing across suspend.

## Test signals
Test probe on both compatibles, route all six stream pairs through XBAR, run S16/S24/S32 at channel counts 1 and 12, change ratio source and SW integer/fraction controls before and during streams, verify lock writes, suspend/resume with SW ratios, and specifically validate all six input/output threshold controls program distinct stream registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.h

## Purpose
This header defines the register map, bit fields, constants, SoC data, and private state structures for the Tegra186/Tegra264 ASRC driver.

## Important APIs, types, and functions
It declares stream register offsets from `TEGRA186_ASRC_CFG` through sample buffer config registers, global offsets through `TEGRA186_ASRC_CYA`, default threshold and compensation constants, fractional precision selections, ratio source values (`ARAD` and `SW`), stream stride/count/limit, and ARAM start addresses for Tegra186 and Tegra264. `struct tegra186_asrc_lane` stores userspace-programmable lane values. `struct tegra_asrc_soc_data` carries the SoC-specific ARAM start address. `struct tegra186_asrc` owns SoC data, six lanes, and a regmap pointer.

## Control flow
There is no executable flow. The `.c` file uses the offset macros to generate per-stream register addresses and regmap access policy, and uses the structures as its private driver state.

## State and persistence
The header describes the persistent software state used to restore hardware after runtime PM. Lane fields mirror ALSA controls and are replayed in `hw_params()` and runtime resume.

## Dependencies and integration points
It is private to the Tegra ASRC implementation and assumes Linux types such as `struct regmap` are available from source includes. The ARAM address constants couple the generic driver to Tegra186/Tegra264 memory maps.

## Risks and edge cases
All stream register arithmetic depends on `TEGRA186_ASRC_STREAM_STRIDE`, `STREAM_MAX`, and `STREAM_LIMIT` staying consistent with hardware. A wrong ARAM start address would cause transfer failures after PM resume. Expanding to more lanes requires resizing `lane[]`, updating DAI/control declarations, and revisiting regmap ranges.

## Test signals
Compile-time use in `tegra186_asrc.c` is the first check. Runtime validation should include verifying register offsets against hardware documentation, regmap access ranges, and PM restore behavior on both SoC data variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.c

## Purpose
This ASoC component driver controls the Tegra186 Digital Speaker Controller, which converts PCM input from AHUB/CIF into oversampled PDM output. It exposes a CIF playback DAI, a DAP playback DAI, DAPM routing to a speaker endpoint, mixer controls for FIFO threshold/conversion/OSR/channel selection, and runtime PM with clock/regcache management.

## Important APIs, types, and functions
`struct tegra186_dspk` stores ALSA control values, the DSPK clock, and regmap. Control getters/setters update `rx_fifo_th`, `osr_val`, `lrsel`, `ch_sel`, `mono_to_stereo`, and `stereo_to_mono`. `tegra186_dspk_hw_params()` programs CIF format and thresholds, computes the DSPK clock rate, sets it, and writes core control fields. Runtime PM functions sync the regcache and enable/disable `clk_dspk`. Regmap access callbacks restrict read/write/volatile registers. Probe sets defaults, acquires `dspk` clock, maps registers, creates cached regmap, registers component/DAIs, and enables PM.

## Control flow
Probe initializes default OSR 64, left LR polarity, stereo channel selection, and mono-to-stereo zero fill. Userspace control changes update only driver memory. On `hw_params()` for the DAP DAI, the driver computes audio/client channel counts from channel select, accepts S16 or S24/S32 formats, clamps FIFO threshold to FIFO depth divided by channels minus one, fills `tegra_cif_conf`, calls `tegra_set_cif()`, computes `dspk_clk = (32 << osr_val) * sample_rate * 4`, sets the clock rate, and writes OSR/channel/LR polarity into `TEGRA186_DSPK_CORE_CTRL`. DAPM enables the RX widget through `TEGRA186_DSPK_ENABLE`.

## State and persistence
Regmap is `REGCACHE_FLAT`; runtime suspend marks it dirty and disables the clock, while resume enables the clock, leaves cache-only, and syncs registers. ALSA control values are stored in driver memory and committed during later `hw_params()` calls; they are not immediately written to hardware except through cached defaults and stream setup.

## Dependencies and integration points
The driver depends on `tegra186_dspk.h`, Tegra CIF helper `tegra_set_cif()`, clocks, regmap MMIO, runtime PM, ASoC DAI/DAPM/control infrastructure, and DT compatible `nvidia,tegra186-dspk`. DAPM route names integrate with AHUB/XBAR playback paths.

## Risks and edge cases
Control writes during an active stream may not take effect until the next `hw_params()`. FIFO threshold is silently clamped and persisted back to state. Clock rate calculation can overflow only at much larger rates than supported, but depends on clock provider acceptance. Channel select and conversion controls can create mismatches between ALSA channels and PDM output expectation. There is no capture path.

## Test signals
Exercise playback at 8-48 kHz, S16/S24/S32, mono and stereo, all OSR settings, left/right/stereo channel selection, conversion controls, FIFO threshold clamping, runtime PM resume after controls are changed, and DAPM route activation from XBAR through `SPK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.h

## Purpose
This header defines Tegra186 DSPK register offsets, bit fields, enums, and private driver state used by the DSPK ASoC component.

## Important APIs, types, and functions
Register offsets cover RX status/interrupt/CIF registers, enable/reset/clock-gate/status registers, and core/codec control. Core control fields include channel select, OSR, and LR polarity masks. Constants define RX FIFO depth, OSR base factor, and the 4:1 DSPK interface clock ratio. Enums describe OSR values, channel selection, and LR polarity. `struct tegra186_dspk` stores control state, clock, and regmap.

## Control flow
There is no executable flow. The `.c` file uses these macros for regmap policies, CIF setup, clock-rate computation, and core-control updates.

## State and persistence
The state struct persists mixer-control choices outside hardware and across runtime PM as long as the device instance exists. Regmap persistence is handled by the implementation's cache.

## Dependencies and integration points
It is private to the DSPK driver and assumes `struct clk` and `struct regmap` are available via source includes. Register definitions must align with hardware and the `tegra186_dspk_regmap` access policy.

## Risks and edge cases
Adding new hardware variants or wider FIFO/rate support requires updating constants and validating the clock formula. Enum ordinal values are written directly into hardware fields, so reordering enums would be a behavioral change.

## Test signals
Compile the DSPK driver, verify macro values against hardware docs, and test that enum values program expected `CORE_CTRL` bits for each ALSA control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.c

## Purpose
This is the Tegra20 AC97 ASoC controller driver. It exposes a stereo 16-bit playback/capture DAI, provides global AC97 bus read/write/reset operations, controls AC97 FIFOs for DMA playback/capture, and registers the Tegra PCM platform.

## Important APIs, types, and functions
Global `workdata` bridges the old ASoC AC97 bus callbacks to the active device. AC97 bus operations are `tegra20_ac97_codec_read()`, `tegra20_ac97_codec_write()`, `tegra20_ac97_codec_reset()`, and `tegra20_ac97_codec_warm_reset()`. Stream operations include trigger helpers for playback/capture and `tegra20_ac97_probe()` to attach DMA data. Regmap callbacks mark control, command, status, FIFO control, and FIFO registers as readable/writeable/volatile/precious. Platform probe configures reset, clock, regmap, codec reset/sync GPIOs, DMA addresses, hardware reset sequencing, AC97 ops, component, and PCM.

## Control flow
Probe gets the AC97 reset control and clock, maps registers, creates regmap, obtains codec reset and sync GPIOs, sets DMA FIFO addresses, asserts controller reset, enables the clock, deasserts reset, registers global AC97 ops, registers the component/DAI, registers PCM, then assigns `workdata`. Codec reads issue a command with read bit and poll `STATUS1_STA_VALID1`. Codec writes issue command/data and poll `CMD_BUSY`. Cold and warm resets toggle GPIO lines and poll codec ready. PCM triggers enable FIFO attention interrupts and controller DAC/stream bits for playback or capture FIFO full signaling for capture.

## State and persistence
The driver uses a cached regmap but has no runtime PM. Hardware stays clocked after probe until remove. AC97 bus state is effectively global through `workdata` and `snd_soc_set_ac97_ops()`, matching the old ASoC AC97 API's single-codec limitation.

## Dependencies and integration points
It depends on Tegra PCM helpers, DMAengine PCM data structures, GPIO descriptors named `nvidia,codec-reset` and `nvidia,codec-sync`, a reset control named `ac97`, a controller clock, regmap MMIO, and compatible `nvidia,tegra20-ac97`. Kconfig selects `SND_SOC_AC97_BUS` and DAS.

## Risks and edge cases
The global `workdata` means only one AC97 controller/codecs path is supported and callback use before assignment would be unsafe. Poll loops time out silently and may return stale readback rather than an error. Probe error handling calls `snd_soc_set_ac97_ops(NULL)` even for early failures. The driver uses non-devm component/PCM registration and manual cleanup. No PM support means idle power may be higher.

## Test signals
Verify AC97 codec reset/warm reset timing, register read/write operations with timeout instrumentation, stereo playback/capture DMA, FIFO underrun/overrun handling, remove cleanup, and failure paths for missing GPIOs/reset/clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.h

## Purpose
This header defines Tegra20 AC97 controller register offsets, bit fields, FIFO controls, and the private state structure used by the AC97 platform driver.

## Important APIs, types, and functions
Offsets include `CTRL`, `CMD`, `STATUS1`, `FIFO1_SCR`, `FIFO_TX1`, and `FIFO_RX1`. Bit fields describe controller enables, cold/warm reset, command address/data/busy fields, status data/valid/ready bits, and FIFO interrupt/attention/force-empty controls. `struct tegra20_ac97` stores clock, playback/capture DMA descriptors, reset control, regmap, and reset/sync GPIO descriptors.

## Control flow
There is no executable flow. The `.c` file uses these definitions for AC97 command transactions, stream trigger enable/disable, DMA FIFO address calculation, and regmap access policy.

## State and persistence
The struct persists controller handles and DMA parameters for the lifetime of the platform device. Register persistence is implemented by the driver's regmap and always-on clock lifecycle.

## Dependencies and integration points
The header includes `tegra_pcm.h` for Tegra PCM/DMA integration. It is private to the Tegra20 AC97 driver and its ASoC/PCM registration path.

## Risks and edge cases
Macros model only the FIFO/channel subset used by the driver; additional AC97 streams would need new definitions and trigger logic. Register bit values must remain consistent with hardware because command read/write paths directly encode fields.

## Test signals
Build the AC97 driver and validate command field encoding, status decoding, and FIFO address offsets against hardware documentation or known-good register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_das.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_das.c

## Purpose
This simple platform driver initializes the Tegra20 Digital Audio Switch. DAS is a mux/crossbar connecting DAP pins and DAC/I2S/AC97 controller endpoints. The driver programs a fixed default routing between DAP1/DAC1 and DAP3/DAC3.

## Important APIs, types, and functions
`struct tegra20_das` only contains a regmap. `tegra20_das_connect_dap_to_dac()` writes a DAP control-select register. `tegra20_das_connect_dac_to_dap()` writes a DAC input/data/clock-select register with the selected DAP for clock and serial data. `tegra20_das_probe()` maps registers, initializes regmap, and programs the default links. `tegra20_das_wr_rd_reg()` defines legal regmap ranges.

## Control flow
Probe allocates state, maps the MMIO resource, creates a cached 32-bit regmap, then writes four default connections: DAP1 to DAC1, DAC1 input/clock from DAP1, DAP3 to DAC3, and DAC3 input/clock from DAP3. No public API is exported for runtime rerouting.

## State and persistence
DAS state is just hardware register programming. Regmap is cached, but there is no runtime PM or explicit restore path in this driver. The fixed routing persists until reset or another agent writes the DAS registers.

## Dependencies and integration points
It depends on DT compatible `nvidia,tegra20-das`, MMIO regmap, and the broader Tegra20 audio topology. Kconfig selects DAS for Tegra20 AC97/I2S users.

## Risks and edge cases
The file comment explicitly says the driver is dumb and does not validate routing. Current code hardcodes a limited default topology and does not support board-specific routes, DAP-to-DAP master/slave setup, or runtime control. Resets after probe could lose routing because no PM restore exists.

## Test signals
Probe on Tegra20, read DAS registers after boot, verify I2S/AC97 paths relying on DAP1/DAC1 and DAP3/DAC3 work, and test behavior after system suspend or controller reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_das.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.c

## Purpose
This is the Tegra20 I2S ASoC controller driver. It provides a stereo playback/capture DAI, programs serial format, sample width, clock/timing, FIFO thresholds, DMA addresses, runtime PM reset/clock sequencing, and optional rate filtering when the audio PLL parent rate is fixed.

## Important APIs, types, and functions
`struct tegra20_i2s` contains the per-device DAI copy, I2S clock, DMA descriptors, regmap, and reset. DAI operations include `tegra20_i2s_set_fmt()`, `tegra20_i2s_hw_params()`, `tegra20_i2s_trigger()`, `tegra20_i2s_startup()`, and `tegra20_i2s_probe()`. Runtime PM uses `tegra20_i2s_runtime_suspend()` and `tegra20_i2s_runtime_resume()`. `tegra20_i2s_filter_rates()` constrains rates to those divisible by the fixed parent clock. Regmap callbacks classify normal, volatile, and precious FIFO registers.

## Control flow
Probe allocates state, copies the DAI template and names it after the device, gets reset and clock, maps registers, creates regmap, fills FIFO DMA addresses, enables runtime PM, registers component/DAI, and registers Tegra PCM. Runtime resume asserts reset, enables clock, waits, deasserts reset, marks regcache dirty, and syncs cached registers; suspend sets cache-only and disables the clock. `set_fmt()` accepts normal bit/frame polarity, master or slave clock provider modes, and DSP_A/DSP_B/I2S/right-justified/left-justified formats. `hw_params()` accepts S16/S24/S32, sets packed FIFO format, computes and sets `i2sclock = rate * channels * sample_size * 2`, writes timing and FIFO thresholds. Triggers enable FIFO1 for playback or FIFO2 for capture.

## State and persistence
Register state is cached across runtime PM. DMA descriptors persist in driver state. The per-device DAI template avoids sharing mutable DAI name across instances. No additional software stream state is tracked beyond hardware and ALSA runtime.

## Dependencies and integration points
It depends on `tegra20_i2s.h`, Tegra PCM helpers, reset/clock providers, regmap MMIO, runtime PM, ASoC DAI/component APIs, and compatible `nvidia,tegra20-i2s`. DAS is selected in Kconfig to route the I2S controller to pins.

## Risks and edge cases
The DAI advertises only S16_LE even though `hw_params()` handles S24/S32, so higher widths may be unreachable without DAI capability changes. Only normal clock polarity is supported. Fixed-parent-rate filtering assumes parent divisibility by `rate * 128`; if no rates match it intentionally filters none. Clock or reset failures during resume disable the clock but leave stream setup to recover. The final hardware `* 2` clock multiplier is Tegra-specific and easy to regress.

## Test signals
Test master/slave formats and all supported serial formats, 8-96 kHz rates, fixed-parent-rate constraints, runtime PM suspend/resume around active controls, DMA playback/capture FIFO enable bits, and whether S24/S32 paths are actually negotiable through ALSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.h

## Purpose
This header defines Tegra20 I2S register offsets, control/status/timing/FIFO bit fields, and the private driver state structure used by the Tegra20 I2S ASoC driver.

## Important APIs, types, and functions
Offsets cover control, status, timing, FIFO scratch/control, PCM/network/TDM controls, and two FIFO data registers. Macros define FIFO enables, loopback/master mode, LRCK polarity, I2S/right/left/DSP bit formats, sample sizes, FIFO packing modes, interrupt/query bits, timing non-symmetric mode, channel bit count, FIFO clear, and FIFO attention levels. `struct tegra20_i2s` stores mutable DAI metadata, clock, DMA descriptors, regmap, and reset.

## Control flow
There is no executable flow. The `.c` file uses these macros in `set_fmt()`, `hw_params()`, trigger helpers, DMA setup, and regmap classification.

## State and persistence
The state struct persists per-controller resources and DMA configuration for the platform-device lifetime. Register persistence is maintained by the implementation's regcache during runtime PM.

## Dependencies and integration points
The header includes `tegra_pcm.h` for Tegra PCM integration and is private to the Tegra20 I2S implementation. The register definitions must align with Tegra20 hardware and DAS routing expectations.

## Risks and edge cases
The header exposes definitions for TDM/PCM/network registers not currently programmed by the driver, so future feature work must validate unused macros. Enum-like bit macros are directly written to hardware fields; bad values would affect serial format and FIFO operation.

## Test signals
Compile the I2S driver, compare register field encodings with hardware documentation, and use register traces from `set_fmt()`/`hw_params()` to validate bit-format, sample-size, and FIFO threshold macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.c

## Purpose
This is the Tegra20 SPDIF ASoC transmitter driver. It exposes a playback-only DAI, programs SPDIF packing/bit mode/FIFO trigger level/clock rate, controls TX enable on PCM triggers, manages runtime PM reset/clock/regcache sequencing, and registers Tegra PCM DMA support.

## Important APIs, types, and functions
`struct tegra20_spdif` stores the output clock, DMA descriptors, regmap, and reset. DAI operations are `tegra20_spdif_probe()`, `tegra20_spdif_hw_params()`, `tegra20_spdif_trigger()`, and `tegra20_spdif_startup()`. `tegra20_spdif_filter_rates()` constrains rates for fixed-parent-rate systems. Runtime PM uses `tegra20_spdif_runtime_suspend()` and `tegra20_spdif_runtime_resume()`. Regmap callbacks classify control/status/FIFO/channel/user registers as readable/writeable/volatile/precious.

## Control flow
Probe allocates state, gets reset and `out` clock, maps MMIO, creates regmap, sets playback DMA to `DATA_OUT`, enables devm runtime PM, registers component/DAI, and registers devm Tegra PCM. Startup optionally adds a rate rule when `nvidia,fixed-parent-rate` is present. `hw_params()` accepts only S16_LE, enables packed 16-bit mode, sets TX FIFO attention to four words to match DMA burst safety, maps sample rates to exact SPDIF output clock rates, sets the clock, and warns if the provider returns a different rate. Triggers set or clear `TX_EN`.

## State and persistence
Register state is cached with regcache across runtime PM. Runtime resume resets hardware and syncs cached registers after enabling the output clock. Playback DMA state is stable after probe. The DAI advertises only 32/44.1/48 kHz even though `hw_params()` has mappings for 88.2/96/176.4/192 kHz.

## Dependencies and integration points
It depends on `tegra20_spdif.h`, Tegra PCM helpers, reset/clock providers, regmap MMIO, runtime PM, ASoC, and DT compatible `nvidia,tegra20-spdif`. The fixed-parent-rate comment describes sharing an audio PLL with I2S/HDMI paths.

## Risks and edge cases
Higher sample-rate cases in `hw_params()` are unreachable unless DAI rates are expanded. Only 16-bit packed PCM is supported. Clock mismatch is warning-only, which may still produce bad HDMI/SPDIF audio. Rate filtering only considers 32/44.1/48 kHz. No capture DAI is registered despite header/register support for RX.

## Test signals
Test playback at 32, 44.1, and 48 kHz, verify `DATA_FIFO_CSR` attention level and `CTRL_TX_EN`, check runtime PM restore, validate fixed-parent-rate constraints with concurrent I2S/HDMI use, and test clock mismatch warnings on non-exact providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.h

## Purpose
This header defines the Tegra20 SPDIF controller's register offsets, bit fields, FIFO/status/data formats, channel/user data registers, and private driver state.

## Important APIs, types, and functions
Offsets cover control/status/strobe/FIFO CSR, data in/out, channel status RX/TX pages, and user status/data FIFOs. Macros describe TX/RX enables, channel/user transmit enables, interrupt/query bits, loopback, packing, 16/20/24/raw bit modes, sticky status bits, strobe settings, RX/TX user/data FIFO clear/attention/count fields, and several layouts for `DATA_OUT`/`DATA_IN`. `struct tegra20_spdif` stores clock, playback/capture DMA descriptors, regmap, and reset.

## Control flow
There is no executable flow. The `.c` file uses a subset of these definitions for playback-only packed 16-bit TX setup, FIFO threshold programming, trigger control, DMA address calculation, and regmap access policy.

## State and persistence
The state struct persists hardware resources and DMA configuration. Register persistence is provided by the implementation's regcache over runtime PM reset/clock cycles.

## Dependencies and integration points
The header includes `tegra_pcm.h` and is private to the Tegra20 SPDIF implementation. It contains more complete RX/channel/user definitions than the current driver actively uses, supporting future expansion or register debugging.

## Risks and edge cases
Two macros reference `SPDIF_DATA_FIFO_CSR_TU_EMPTY_COUNT_SHIFT` and `SPDIF_DATA_FIFO_CSR_TX_EMPTY_COUNT_SHIFT` without the `TEGRA20_` prefix, which would fail if those masks were compiled in active code. Current `.c` usage does not reference those masks. The broad register model includes RX support that is not surfaced by the driver.

## Test signals
Build coverage should catch any newly used typo macros. Register-level tests should verify packed 16-bit data layout, FIFO attention fields, sticky status clearing, and channel/user register offsets against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.h -->
