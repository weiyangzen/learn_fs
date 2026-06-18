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
