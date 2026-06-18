# subset-b-006506 Research

Grouped source research for Freescale/NXP ASoC eASRC, ESAI, MICFIL, MQS, QMC audio, and RPMSG audio drivers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c` implements the NXP Enhanced Asynchronous Sample Rate Converter ASoC driver. It exposes a CPU DAI for playback/capture sample-rate conversion, registers the common ASRC m2m platform hooks, loads coefficient firmware, programs resampler and prefilter coefficient memories, manages up to four eASRC contexts with slot allocation, and integrates runtime/system PM around the eASRC memory clock and regmap cache. The source was read as a complete 2425-line file.

## Important APIs, Types, and Functions

Important ALSA controls include per-context dither, IEC958 validity, IEC958 bits-per-sample, and IEC958 channel-status register get/put handlers. Core coefficient and ratio helpers are `fsl_easrc_set_rs_ratio`, `fsl_easrc_normalize_rates`, `fsl_easrc_coeff_mem_ptr_reset`, `fsl_easrc_resampler_config`, `fsl_easrc_normalize_filter`, `fsl_easrc_write_pf_coeff_mem`, and `fsl_easrc_prefilter_config`. Context lifecycle is handled by `fsl_easrc_request_context`, `fsl_easrc_release_context`, `fsl_easrc_config_context`, `fsl_easrc_start_context`, and `fsl_easrc_stop_context`. DAI entry points are `startup`, `trigger`, `hw_params`, `hw_free`, and `dai_probe`. m2m integration is provided through `fsl_easrc_m2m_prepare`, `m2m_start`, `m2m_stop`, `m2m_calc_out_len`, `m2m_get_maxburst`, pair suspend/resume, ratio modification, and capability reporting.

## Control Flow

Probe allocates `struct fsl_asrc` plus `struct fsl_easrc_priv`, maps registers, creates a regmap, requests the IRQ, obtains the `mem` clock, reads `fsl,asrc-rate`, `fsl,asrc-format`, and `firmware-name`, initializes common ASRC callbacks, enables runtime PM, registers the eASRC DAI component and common ASRC platform component, then initializes the m2m device. Runtime resume enables the memory clock, syncs the regcache, loads firmware once per resume epoch, programs global resampler coefficients, and restores active context coefficient state. PCM `hw_params` requests a context, derives input/output rates and formats depending on playback versus capture, writes format fields, configures ratio, prefilter, slot allocation, watermarks, and FIFO organization. Trigger start enables FIFO watermark DMA requests and the context; trigger stop requests a run stop, drains output FIFO samples until run-stop-done or timeout, then clears enable/DMA bits.

## State and Persistence Behavior

Driver state lives in the platform device drvdata, the common `fsl_asrc` object, `fsl_easrc_priv`, and per-context `fsl_easrc_ctx_priv`. Firmware is requested by name and kept as pointers into the firmware image for interpolation and prefilter tables. Runtime suspend sets regcache cache-only, disables `mem_clk`, and marks `firmware_loaded` false so coefficient RAM is reloaded on resume. Context allocation state is protected with `easrc->lock`, including `easrc->pair[]`, `channel_avail`, and the two-slot-per-pipe allocation table. No file-backed persistence is present; persistent behavior is hardware register state plus regcache and loaded firmware pointers.

## Dependencies and Integration Points

The file depends on Linux platform, firmware, clk, IRQ, regmap, runtime PM, DMA, and ALSA ASoC/PCM APIs. It includes `fsl_easrc.h` and `imx-pcm.h`, and it registers with the shared Freescale ASRC layer through callbacks in `struct fsl_asrc` and `fsl_asrc_m2m_init/exit/suspend/resume`. Device-tree bindings provide compatible `fsl,imx8mn-easrc`, ASRC output rate/format, firmware name, clocks, IRQ, and DMA channel names like `ctx0_rx` and `ctx0_tx`.

## Risks and Edge Cases

The firmware format is trusted after `request_firmware`; malformed counts or coefficient layout can make the parsed pointer arithmetic unsafe unless validated elsewhere. Ratio arithmetic uses fixed-point shifts and `do_div`, so extreme rates, taps, or ratio modifiers can overflow or exceed hardware range. Slot allocation splits large channel counts across processing slots and depends on prefilter memory accounting; off-by-one errors directly affect channel routing. `fsl_easrc_stop_context` has a bounded drain loop and only warns on timeout. The source snapshot also shows apparent compile-risk typos such as an extra brace in the DAI driver initializer; those should be checked against the actual build tree.

## Test Signals

Useful signals include kernel build coverage with `CONFIG_SND_SOC_FSL_EASRC`, device-tree probe with valid firmware, ALSA PCM playback and capture at all constrained rates, IEC958 capture format tests, m2m conversion tests for integer/float and rate-up/rate-down paths, suspend/resume while contexts are active, IRQ injection or stress tests for FIFO overrun/underrun, and DMA channel-name verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h` is the private hardware contract for the NXP eASRC driver. It defines the register map, bitfield encoders, FIFO and coefficient-memory constants, firmware binary record layouts, per-format metadata, per-context parameters, slot allocation state, and top-level eASRC private state consumed by `fsl_easrc.c`. The source was read as a complete 655-line file.

## Important APIs, Types, and Functions

The header is macro and type focused. Register-address helpers include `REG_EASRC_WRFIFO`, `RDFIFO`, `CC`, `CCE1`, `CCE2`, `CIA`, `DPCS0/1Rx`, `COC`, `COA`, `SFS`, ratio registers, coefficient FIFOs, IRQ registers, channel-status registers, and debug registers. Bitfield macros encode context enable/stop/watermarks, input/output format, sample positions, prefilter stage taps, access organization, datapath slot channels and memory addresses, ratio values, coefficient writes, and IRQ masks. Types include `enum easrc_word_width`, packed firmware records `asrc_firmware_hdr`, `interp_params`, `prefil_params`, `fsl_easrc_data_fmt`, `fsl_easrc_io_params`, `fsl_easrc_slot`, `fsl_easrc_ctx_priv`, and `fsl_easrc_priv`.

## Control Flow

There is no executable flow in this header. It supplies the compile-time constants used by the implementation when probe initializes regmap ranges, firmware parsing maps coefficient arrays, `hw_params` translates PCM formats into hardware fields, and runtime resume reloads coefficient memories.

## State and Persistence Behavior

The state definitions are all in-memory driver state. `fsl_easrc_ctx_priv` persists per active ASRC pair and stores normalized rates, sample formats, filter taps, coefficient pointers, initialization modes, ratio adjustments, and sample accounting. `fsl_easrc_priv` persists for the platform device and stores slot ownership, firmware pointers, firmware name, selected resampler taps, IEC958 bps values, a constant coefficient, and a firmware-loaded flag. Packed firmware structs define the expected persistent firmware image ABI but do not own storage.

## Dependencies and Integration Points

The header includes ALSA `asound.h`, i.MX DMA definitions, and `fsl_asrc_common.h`, so it is tied to the common Freescale ASRC pair model and `IN`/`OUT` direction constants. It is used directly by `fsl_easrc.c` for register programming and by any compile unit that needs eASRC-private format or firmware declarations.

## Risks and Edge Cases

Several macros are ABI-critical: any bit shift, mask, or packed layout change can break hardware programming or firmware parsing. The packed firmware structs contain large fixed coefficient arrays, so firmware producers must match the exact record shape. The source snapshot includes apparent typo hazards such as duplicate `EASRC_DPCS0R3_ST2_MA_SHIFT` and `EASRC_IRQC_OERM(v)` masking with `EASRC_IEQC_OERM_MASK`, which should be verified by build coverage.

## Test Signals

Build tests should include all eASRC users with warnings enabled. Runtime tests should indirectly cover these definitions by reading/writing all regmap ranges, loading a known-good firmware image, exercising 16/20/24/32-bit and IEC958 formats, and validating suspend/resume coefficient reload. Static checks for macro spelling, duplicate definitions, and packed struct sizes would be high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.c` implements the Freescale/NXP ESAI CPU DAI driver for i.MX/VF610-class SoCs. It configures ESAI serial audio clocks, dividers, formats, TDM slots, FIFO/DMA behavior, xrun reset handling, regmap caching, and runtime PM. The source was read as a complete 1211-line file.

## Important APIs, Types, and Functions

Key private types are `struct fsl_esai_soc_data` with the `reset_at_xrun` quirk and `struct fsl_esai` with DMA data, clocks, work item, spinlock, FIFO/slot masks, channel counters, clock rates, mode flags, and name. Important functions include `esai_isr`, `fsl_esai_divisor_cal`, `fsl_esai_set_dai_sysclk`, `fsl_esai_set_bclk`, `fsl_esai_set_dai_tdm_slot`, `fsl_esai_set_dai_fmt`, `fsl_esai_startup`, `fsl_esai_hw_params`, `fsl_esai_hw_init`, `fsl_esai_register_restore`, `fsl_esai_trigger_start`, `fsl_esai_trigger_stop`, `fsl_esai_hw_reset`, `fsl_esai_trigger`, `fsl_esai_probe`, and runtime suspend/resume.

## Control Flow

Probe allocates private state, maps registers, initializes regmap, obtains core/extal/fsys/spba clocks, requests the shared IRQ, reads FIFO depth and synchronous-mode device-tree properties, sets DMA addresses to ETDR/ERDR, enables runtime PM, initializes ESAI hardware, clears slot masks, initializes the i.MX PCM DMA platform, registers the ASoC component/DAI, and sets up the xrun reset work item. DAI format setup writes protocol polarity, alignment, and clock provider bits. Sysclk and bclk setup derive HCK and SCK through PSR/PM/FP divisors. `hw_params` computes slot width, bclk, channel-to-pin count, FIFO watermark and enable masks, sample word size, network mode, and port control reset release. Trigger start enables FIFO, writes initial TX words, enables TE/RE, writes slot masks in a specific SMB then SMA sequence, and enables exception interrupts. Trigger stop disables exception interrupts, TE/RE, slot masks, and FIFO.

## State and Persistence Behavior

State is per platform device and cached in `struct fsl_esai`. Runtime PM makes the regmap cache-only on suspend and restores it on resume after enabling clocks. `fsl_esai_hw_reset` saves FIFO control state, stops TX/RX, reinitializes hardware, forces personal reset bits, syncs regcache, releases resets, and restarts previously enabled directions. The work item is serialized against trigger paths with a spinlock. No disk persistence exists.

## Dependencies and Integration Points

The driver depends on Linux clk, IRQ, platform, OF, pm_runtime, regmap, ALSA ASoC, DMA engine PCM, `fsl_esai.h`, and `imx-pcm.h`. Device-tree compatibles map to SoC data for `fsl,imx35-esai`, `fsl,vf610-esai`, and `fsl,imx6ull-esai`. It integrates with machine drivers through standard DAI ops and with DMA through `imx_pcm_dma_init` and `snd_soc_dai_init_dma_data`.

## Risks and Edge Cases

Clock divisor calculation rejects odd or out-of-range ratios and only approximates within a 0.1 percent threshold; unsupported parent clocks or missing assigned clocks cause format setup failures. Xrun reset depends on SoC quirk data and asynchronous work. Synchronous mode changes symmetry constraints globally on the DAI driver object, which can surprise shared-driver assumptions. The source snapshot shows repeated `SND_SOC_DAIFMT_I2S` case and duplicate-looking reg defaults, so compile and review checks matter.

## Test Signals

Build with ESAI enabled, probe on each compatible, DMA playback/capture at 8 kHz to 192 kHz, all supported formats, TDM slot masks, provider/consumer clock modes, synchronous full-duplex operation, xrun recovery, runtime PM suspend/resume with active and idle streams, and regmap debugfs access after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.h` defines the ESAI register map, directional register helpers, bitfields, slot-mask encoders, GPIO control constants, and clock/divider IDs used by `fsl_esai.c`. The source was read as a complete 351-line file.

## Important APIs, Types, and Functions

This header has no functions or structs. Important macros include `REG_ESAI_xFCR`, `REG_ESAI_xFSR`, `REG_ESAI_xCR`, `REG_ESAI_xCCR`, `REG_ESAI_xSMA`, and `REG_ESAI_xSMB`, which abstract TX/RX register selection. Bitfield macros cover ECR enable/reset/clock input-output bits, ESR and SAISR status bits, FIFO configuration/status, SAICR synchronous mode, transmit/receive control fields, clock control dividers and polarities, slot mask split across SMA/SMB, and PRRC/PCRC port control. It also defines HCK source IDs and divider IDs used by DAI sysclk configuration.

## Control Flow

The header contributes no runtime flow. `fsl_esai.c` uses these definitions to translate ASoC DAI format, TDM, sysclk, bclk, trigger, IRQ, and PM events into ESAI register writes.

## State and Persistence Behavior

No storage is owned by this header. The macros encode the register state cached by the implementation's regmap and restored across runtime PM. Register layout and bit positions are effectively a hardware ABI for all supported ESAI SoCs.

## Dependencies and Integration Points

The header is included by the ESAI DAI implementation and is tied to ASoC clock identifiers passed to `.set_sysclk` and `.set_fmt`. It also references i.MX/Freescale register-level concepts such as HCKT/HCKR, PRRC/PCRC GPIO mode, and TX/RX slot masks.

## Risks and Edge Cases

Bitfield macros perform shifts and masks directly, so invalid caller values can truncate silently. Slot and channel enable macros depend on valid channel counts. Macro changes have broad impact because they drive IRQ decoding, FIFO reset, clock derivation, and slot activation. Compile coverage should catch syntax issues, but behavioral mismatches require hardware tests.

## Test Signals

Compile the ESAI driver, run register-level smoke tests through normal PCM paths, validate DAI sysclk and bclk divider programming, check TDM slot masks spanning SMA and SMB, and verify IRQ status decoding for underrun/overrun conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_esai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.c` implements the NXP PDM microphone interface capture DAI. It configures MICFIL clocks, decimation quality, DC remover and output gain/range controls, DMA capture, optional DSD decimation bypass, HWVAD voice activity detection, IRQ handling, regmap variants, and runtime PM for i.MX8/i.MX9-class SoCs. The source was read as a complete 1670-line file.

## Important APIs, Types, and Functions

Private types include `enum quality`, `struct fsl_micfil`, and `struct fsl_micfil_soc_data`. ALSA controls are implemented for MICFIL quality, HWVAD enablement/init mode/high-pass/ZCD parameters, DC remover, output channel range or signed volume, HWVAD gains, detector timing, and read-only `VAD Detected`. Key helpers include `micfil_get_max_range`, `micfil_range_set`, `micfil_set_quality`, control get/put handlers, `fsl_micfil_use_verid`, `fsl_micfil_reset`, `fsl_micfil_configure_hwvad_interrupts`, HWVAD init/enable/disable helpers, `fsl_micfil_reparent_rootclk`, `fsl_micfil_hw_params`, `hw_free`, DAI/component probe, regmap access predicates, four IRQ handlers, probe/remove, and runtime PM callbacks.

## Control Flow

Probe obtains `ipg_clk_app` and `ipg_clk`, PLL clocks, optional `clkext3`, derives a constrained rate list, maps registers, selects a v1/v2 regmap config, validates `fsl,dataline`, requests four IRQ lines, initializes DMA RX parameters, enables runtime PM, optionally reads VERID/PARAM, switches regcache to cache-only, registers DMAengine PCM, adjusts the DAI format mask from SoC data, and registers the component/DAI. DAI probe sets default quality, output gain/range defaults, DC remover bypass, DMA data, and FIFO watermark. `hw_params` disables the module, enables channels, reparents and sets root clock, handles PCM versus DSD bypass clocking, writes quality/CLKDIV/CICOSR/VAD channel fields, and sizes DMA burst/peripheral config. Trigger start soft-resets, selects DMA request mode, enables PDM and error IRQs, and optionally enables HWVAD; stop disables HWVAD and the module.

## State and Persistence Behavior

Runtime state is held in `struct fsl_micfil`, including quality, DC remover mode, VAD settings, VAD detected flag, version/parameter discovery, mclk enable flag, and decimation bypass. Regmap cache is set cache-only during runtime suspend and synced on resume. `mclk_flag` prevents unnecessary app-clock enablement while idle and ensures active capture resumes with clocks restored. HWVAD detection persists as an in-memory flag exposed through an ALSA control until reset by the next VAD enable path.

## Dependencies and Integration Points

The driver depends on clk, OF/platform, IRQ, regmap, pm_runtime, DMAengine PCM, ALSA ASoC, i.MX SDMA peripheral config, `fsl_micfil.h`, and `fsl_utils.h` helpers for PLL clocks and rate constraints. Device-tree compatibles select i.MX8MM, i.MX8MP, i.MX93, and i.MX943 data including FIFO depth, FIFO offset, formats, eDMA usage, VERID support, and volume model.

## Risks and Edge Cases

Clock calculation differs for PCM and DSD bypass and relies on PLL reparenting; bad parents or unsupported rates break capture setup. HWVAD is only safe when the filter is not busy, but trigger-time sequencing must ensure that condition. Dataline validation only checks the mask against SoC support. The v2 FIFO offset changes data register addresses for i.MX943 and must match hardware. The source snapshot shows a duplicated local declaration in `hwvad_get_enable`, which is a build-risk signal to verify.

## Test Signals

Build with MICFIL enabled, probe all compatible SoC data, capture at constrained rates and 1 to 8 channels, test S16/S32/DSD formats where advertised, verify DMA burst sizing for SDMA and eDMA, exercise every ALSA control under runtime PM, run HWVAD interrupt notification tests, and suspend/resume during and after capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.h` defines the MICFIL hardware register map, control/status bitfields, FIFO and IRQ constants, HWVAD bitfields, and version/parameter data structures consumed by `fsl_micfil.c`. The source was read as a complete 214-line file.

## Important APIs, Types, and Functions

The header is macro and type focused. Register constants cover CTRL1/CTRL2, status, FIFO control/status, eight data channel registers, DC/output controls, FSYNC, VERID/PARAM, and HWVAD control/status/config/data/ZCD registers. Bitfields cover module disable/reset/enable, DMA/IRQ selection, channel enablement, quality selector, decimation bypass, CIC OSR, low-frequency and FIFO error flags, per-channel DC remover configuration, VERID/PARAM feature bits, HWVAD channel/CIC/init/interrupt/reset/enable fields, HWVAD filters/gains/ZCD/status, output gain shifts, channel/FIFO/IRQ counts, and DMA burst constants. Types are `struct fsl_micfil_verid` and `struct fsl_micfil_param`.

## Control Flow

There is no executable flow. The implementation uses this header for regmap access policies, ALSA control bit positions, IRQ status decoding, reset sequencing, HWVAD configuration, and hardware capability parsing.

## State and Persistence Behavior

No storage is owned here. The two structs define in-memory copies of hardware version and parameter registers. Register constants represent hardware state cached by regmap and restored across runtime PM.

## Dependencies and Integration Points

The header assumes Linux `BIT`/`GENMASK` macros are available through including translation units. It is integrated only with the MICFIL implementation and the SoC-specific data that chooses which registers are readable, writable, volatile, or offset.

## Risks and Edge Cases

Wrong bitfields can corrupt audio capture setup, HWVAD behavior, or write-one-to-clear status handling. The `MICFIL_DC_CUTOFF_152Hz` spelling differs in case from common all-caps style but is only a macro name. FIFO constants must remain aligned with hardware-reported PARAM values for newer SoCs.

## Test Signals

Compile MICFIL with all compatible data, verify regmap access tables accept every defined register needed by controls and IRQs, compare VERID/PARAM decoding with hardware documentation, and run capture/HWVAD tests that force status flag clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_micfil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_mqs.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_mqs.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_mqs.c` implements the Freescale/NXP Medium Quality Sound codec/DAI driver. MQS is a simple stereo S16 playback endpoint that programs enable, reset, oversample, and clock-divider fields located either in the module register block, an IOMUXC GPR syscon register, or an SCMI/System Manager controlled register. The source was read as a complete 471-line file.

## Important APIs, Types, and Functions

Key types are `enum reg_type`, `struct fsl_mqs_soc_data`, and `struct fsl_mqs`. SoC data records the register backend, optional SCMI index, control offset, and masks/shifts for enable, reset, oversample, and divider fields. Important functions are `fsl_mqs_sm_read`, `fsl_mqs_sm_write`, `fsl_mqs_hw_params`, `fsl_mqs_set_dai_fmt`, `fsl_mqs_startup`, `fsl_mqs_shutdown`, `fsl_mqs_probe`, runtime suspend/resume, and the platform driver registration. The DAI supports two playback channels, 44.1/48 kHz, S16_LE, LEFT_J, normal bit/frame polarity, and codec bit/frame clock consumer mode.

## Control Flow

Probe selects SoC data from OF match. For GPR-backed SoCs it resolves a `gpr` phandle and gets a syscon regmap. For System Manager SoCs it creates a custom regmap backed by SCMI misc control get/set calls. For own-register SoCs it maps MMIO and initializes an MMIO-clock regmap, then obtains the `core` clock. All variants obtain `mclk`, enable runtime PM, and register the ASoC component and DAI. Startup sets the enable bit. `hw_params` reads `mclk`, computes a divider for fixed 32x oversampling and repeat rate 8, writes divider and oversample fields when exact and in range, and logs an error otherwise. Shutdown clears enable. Runtime suspend saves the control register and disables clocks; resume enables clocks and restores the saved control word.

## State and Persistence Behavior

Per-device state stores the selected regmap, clocks, SoC data, and saved `reg_mqs_ctrl`. The saved control word is the only software persistence across runtime PM. Regcache is disabled for the own regmap; GPR/SM accesses are direct through their regmap backends. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on clk, syscon, i.MX IOMUXC GPR definitions, optional SCMI misc firmware controls, runtime PM, and ALSA ASoC. Device-tree compatibles include i.MX8QM, i.MX6SX, i.MX93, i.MX95 AON/NETC, and i.MX943 AON/wakeup variants.

## Risks and Edge Cases

The runtime PM callbacks unconditionally operate on `ipg`, but GPR and SM variants do not initialize `ipg` in probe, so the actual PM behavior should be checked for those variants. `hw_params` logs an invalid divider but returns success, which may allow playback to start with stale divider state. SCMI access only works when `CONFIG_IMX_SCMI_MISC_DRV` is enabled. Format support is intentionally narrow.

## Test Signals

Build with each compatible enabled, probe all register backend types, verify runtime PM for own/GPR/SM backends, run 44.1 and 48 kHz stereo S16 playback, validate divider register values from known mclk rates, and test failure handling when SCMI misc control support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_mqs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c` implements an ASoC component and dynamic DAI set for audio over Freescale QUICC Engine/CPM QMC transparent channels. It maps one or more QMC channels into ALSA PCM playback/capture streams, supports interleaved and non-interleaved access models, derives hardware constraints from QMC time-slot masks, submits cyclic QMC read/write transfers, and reports PCM position by completed periods. The source was read as a complete 974-line file.

## Important APIs, Types, and Functions

Private types are `struct qmc_dai`, `struct qmc_audio`, and `struct qmc_dai_prtd`. PCM platform callbacks include `qmc_audio_pcm_new`, `open`, `close`, `hw_params`, `trigger`, `pointer`, and `of_xlate_dai_name`. Transfer helpers include `qmc_audio_pcm_write_submit`, `qmc_audio_pcm_write_complete`, `qmc_audio_pcm_read_submit`, and `qmc_audio_pcm_read_complete`. DAI helpers include `qmc_dai_get_index`, `qmc_dai_get_data`, format/channel hardware rules, interleaved/non-interleaved constraint setup, `qmc_dai_startup`, `qmc_dai_hw_params`, `qmc_dai_trigger`, `qmc_audio_formats`, `qmc_audio_dai_parse`, and `qmc_audio_probe`.

## Control Flow

Probe counts child nodes, allocates matching `qmc_dai` and `snd_soc_dai_driver` arrays, parses each child `reg` and `fsl,qmc-chan` phandles, validates QMC transparent mode, consistent TX/RX slot counts and frame rates, and monotonic timeslot ordering, then builds DAI names, rates, channel ranges, and format masks. Component registration exposes all generated DAIs. PCM open installs hardware limits and allocates per-substream private data. DAI startup attaches the selected QMC DAI and installs interleaved constraints for a single QMC channel or non-interleaved constraints for multiple channels. PCM `hw_params` computes per-channel DMA buffer slices. DAI `hw_params` configures capture QMC max RX buffer size. PCM trigger start submits two initial read/write periods; completion callbacks submit the next period, wrap DMA addresses, update `buffer_ended`, and notify ALSA. DAI trigger starts/stops/resets the QMC channels.

## State and Persistence Behavior

Device state is devm-managed and persists for the platform device. Substream state is allocated on open and freed on close. `qmc_dai` tracks available channels plus currently used TX/RX channel counts. `qmc_dai_prtd` tracks buffer address windows, per-period size, channel count, current DMA address, and completed frame pointer. There is no regmap or runtime PM state in this driver; persistence is runtime memory and QMC channel state.

## Dependencies and Integration Points

The file depends on DMA mapping, OF platform, ALSA ASoC/PCM, and `soc/fsl/qe/qmc.h`. It integrates tightly with the QMC channel API: `qmc_chan_count_phandles`, `devm_qmc_chan_get_byphandles_index`, `qmc_chan_get_info`, `qmc_chan_get_ts_info`, `qmc_chan_set_param`, `qmc_chan_start`, `qmc_chan_stop`, `qmc_chan_reset`, `qmc_chan_write_submit`, and `qmc_chan_read_submit`. The OF compatible is `fsl,qmc-audio`.

## Risks and Edge Cases

The driver assumes completion callbacks can safely resubmit immediately and call `snd_pcm_period_elapsed`. Stop/pause paths do not explicitly cancel already submitted PCM-side transfers; channel stop/reset semantics must handle that. Interleaved versus non-interleaved constraints depend on QMC channel count and exact time-slot math. The source snapshot shows a doubled opening brace in `qmc_dai_constraints_noninterleaved`, a likely compile issue to verify. Little-endian PCM formats are intentionally skipped by `qmc_audio_formats`, so machine-driver expectations must match.

## Test Signals

Build with QMC support, probe a device tree with one and multiple QMC channels, verify generated DAI names through phandle translation, run interleaved and non-interleaved playback/capture, check period pointer progression and wraparound, test unsupported format/channel combinations, and exercise start/stop/suspend-like stop paths while transfers are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c` implements an ASoC CPU DAI facade for NXP RPMsg audio channels. It presents playback/capture capabilities to ALSA, sizes DMA buffers for normal or low-power-audio operation, switches audio PLL parents based on sample-rate family, manages optional clocks, and customizes DAI names/caps from device tree and SoC data. The source was read as a complete 353-line file.

## Important APIs, Types, and Functions

Important functions are `fsl_rpmsg_hw_params`, `fsl_rpmsg_hw_free`, `fsl_rpmsg_startup`, `fsl_rpmsg_probe`, `fsl_rpmsg_remove`, and runtime suspend/resume. Static data includes `fsl_rpmsg_rates`, the rate constraint list, the base `fsl_rpmsg_dai`, the ASoC component, and SoC capability tables for i.MX7ULP, i.MX8MM, i.MX8MN, i.MX8MP, i.MX93, and i.MX95. Constants define large low-power playback/capture buffer sizes.

## Control Flow

Startup constrains PCM rates to a broad explicit list. `hw_params` walks up from `mclk` to find a parent matching `pll8k` or `pll11k`; if found, it selects the 8 kHz-family PLL when the requested rate is divisible by 8000, otherwise the 11.025 kHz-family PLL, and enables `mclk` once per active stream direction. `hw_free` disables `mclk` for that stream. Probe copies the base DAI, applies SoC-specific rates/formats, chooses the DAI name from `fsl,rpmsg-channel-name` or a default, special-cases `rpmsg-micfil-channel` capture capabilities, sets LPA or default DMA buffer sizes, obtains optional clocks, enables runtime PM, and registers the component. Runtime resume enables `ipg` and `dma`; suspend disables them.

## State and Persistence Behavior

Per-device state is `struct fsl_rpmsg`, holding optional clocks, optional child card device, SoC data, active `mclk_streams` bitmask, low-power flags, and per-direction buffer sizes. Stream clock state persists across `hw_params`/`hw_free` through the bitmask. No register cache or file-backed persistence is present.

## Dependencies and Integration Points

The file depends on Linux clk, runtime PM, OF, RPMsg headers, ALSA ASoC/PCM, DMAengine PCM, `fsl_rpmsg.h`, and `imx-pcm.h` for default DMA buffer sizing. It integrates with remote-processor audio through named RPMsg channels, though this file itself is the CPU DAI-facing side rather than the RPMsg message transport implementation.

## Risks and Edge Cases

`clk_prepare_enable` is called on optional clocks that may be NULL depending on clock API behavior, so platform coverage matters. PLL parent switching mutates `rate` via `do_div`; the divisibility test is concise but easy to misread. `fsl,rpmsg-channel-name` changes DAI identity and caps, so machine-driver and remote firmware names must match. LPA buffer sizes are large and affect memory pressure.

## Test Signals

Build with RPMsg audio, probe every compatible data path, verify DAI names from device tree, open normal and `rpmsg-micfil-channel` capture streams, test 8 kHz-family and 44.1 kHz-family PLL switching, ensure `mclk_streams` balances across playback/capture hw_params/free, and verify runtime PM clock enable/disable on platforms with absent optional clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h` declares the private data structures shared by the RPMsg audio CPU DAI implementation. It captures per-SoC advertised rates/formats and per-device clock, low-power-audio, and buffer-size state. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

The header defines `struct fsl_rpmsg_soc_data` with `rates` and `formats`, and `struct fsl_rpmsg` with `ipg`, `mclk`, `dma`, `pll8k`, `pll11k`, `card_pdev`, `soc_data`, `mclk_streams`, `force_lpa`, `enable_lpa`, and `buffer_size[2]`. It has no functions.

## Control Flow

There is no executable flow. `fsl_rpmsg.c` populates these structures during probe, consults `soc_data` to configure the copied DAI driver, tracks stream clock ownership through `mclk_streams`, and uses buffer-size fields when integrating with the DMA/platform layer.

## State and Persistence Behavior

The header defines runtime-only platform-device state. `mclk_streams` persists while streams are configured, low-power flags persist for the device lifetime, and `buffer_size` persists as per-direction configuration. No state is file-backed.

## Dependencies and Integration Points

The header relies on Linux clock and platform-device types through the including `.c` file. Its structures are the direct contract between device-tree match data and the RPMsg DAI implementation.

## Risks and Edge Cases

The structure contains optional clock pointers, so users must handle NULL or error pointers consistently. `force_lpa` is declared but not actively used in the read implementation, which may indicate planned or out-of-tree integration. Rate fields use `int` ALSA rate masks while formats use `u64`.

## Test Signals

Compile the RPMsg driver, verify each compatible's `soc_data` is applied, check low-power buffer sizing from device tree, and run stream open/close tests that prove `mclk_streams` state is balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h -->
