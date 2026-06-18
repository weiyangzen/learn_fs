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
