# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.c

## Purpose
`fsl_ssi.c` is the Freescale SSI ASoC CPU DAI driver for MPC8610 and i.MX SSI blocks. It supports I2S, left-justified, DSP A/B, AC97, synchronous/asynchronous operation, DMA or FIQ stream filtering, single/dual/dynamic FIFO use, TDM masks, legacy machine-card instantiation, AC97 codec register access, debug IRQ statistics, and system sleep register caching.

## Important APIs, Types, And Functions
The platform driver is `fsl_ssi_driver`, matched by `fsl_ssi_ids`. The core private state is `struct fsl_ssi`, with SoC policy in `struct fsl_ssi_soc_data` and cached per-direction register bits in `struct fsl_ssi_regvals`.

Key functions are `fsl_ssi_probe`, `fsl_ssi_probe_from_dt`, `fsl_ssi_imx_probe`, `fsl_ssi_hw_init`, `fsl_ssi_hw_clean`, `fsl_ssi_startup`, `fsl_ssi_shutdown`, `fsl_ssi_set_bclk`, `fsl_ssi_hw_params`, `fsl_ssi_hw_free`, `_fsl_ssi_set_dai_fmt`, `fsl_ssi_set_dai_fmt`, `fsl_ssi_set_dai_tdm_slot`, `fsl_ssi_trigger`, `fsl_ssi_config_enable`, `fsl_ssi_config_disable`, `fsl_ssi_isr`, `fsl_ssi_suspend`, and `fsl_ssi_resume`. AC97 access is implemented through `fsl_ssi_ac97_read`, `fsl_ssi_ac97_write`, and `fsl_ssi_ac97_ops`.

## Control Flow
Probe parses DT for IPG clock naming, AC97 mode, synchronous mode, DMA vs FIQ, FIFO depth, dual/dynamic FIFO SDMA type, and legacy card creation. It selects the normal or AC97 DAI template, maps registers, adapts regmap max register for i.MX21-class SSI, requests the IRQ, applies symmetric constraints in synchronous mode, sets FIFO watermarks/maxburst from FIFO depth, initializes i.MX clocks and PCM backend, sets AC97 ops when needed, registers the component, requests IRQ for DMA mode, creates debugfs, initializes SSI registers, and optionally registers an old-style sound-card or AC97 codec platform device.

Runtime stream setup enables the register clock and adds even-period constraints for dual/dynamic FIFO. `set_fmt` programs SCR/STCR/SRCR for audio format, polarity, clock provider mode, I2S/network mode, and synchronous mode. `set_tdm_slot` programs frame slot count, masks STMSK/SRMSK while temporarily enabling SSIEN, and stores slot metadata. `hw_params` optionally calculates and enables baudclk for master mode, handles word length and I2S/network overrides, and configures dynamic FIFO SDMA peripheral parameters by channel count. Trigger starts by refreshing AC97 slot status when needed and calling `fsl_ssi_config_enable`; stop calls `fsl_ssi_config_disable`.

`fsl_ssi_config_enable` clears the FIFO, writes cached SRCR/STCR/SIER bits either for both directions on offline-config SoCs or for the active direction on online-config SoCs, primes TX DMA by waiting for FIFO fill, then enables SCR bits and marks the stream active. Disable computes shared-bit exclusions so stopping one direction does not break the other, handles offline-config restrictions, clears SIER/SxCR bits, and clears FIFO.

## State And Persistence
`struct fsl_ssi` persists DAI format, active stream mask, synchronous flag, DMA/FIQ and FIFO mode flags, clock handles, baudclk stream mask, slot settings, cached register values, DMA/FIQ parameters, physical address, legacy card device, debug stats, FIFO watermarks, AC97 mutex, and SDMA peripheral config. System suspend caches `SFCSR` and `SACNT`, marks regcache dirty/cache-only, and resume restores FIFO watermarks/AC97 control before syncing regcache. AC97 register access uses a global `fsl_ac97_data` pointer and a mutex because AC97 bus ops lack per-instance context.

## Dependencies And Integration Points
The driver integrates with ALSA ASoC, DMAEngine PCM, `imx-pcm` DMA/FIQ backends, AC97 bus operations, OF platform legacy card registration, Linux clock framework, regmap, debugfs via `fsl_ssi_dbg.c`, and register definitions from `fsl_ssi.h`.

## Risks And Edge Cases
Offline-config SoCs cannot safely reprogram critical bits while SSIEN is set, so the cached register-bit merge/exclusion logic is crucial when both streams are active. Master BCLK generation requires a valid baudclk, must stay below IPG/5, and searches dividers with approximate matching. AC97 mode has hardware limitations described in the file header, including fixed practical 48 kHz capture and unreliable status polling, so it uses fixed delays. Dynamic FIFO mode mutates cached FIFO-enable bits based on mono vs multi-channel layout. Legacy card registration and global AC97 data are single-instance-sensitive.

## Test Signals
Exercise I2S provider/consumer, synchronous full-duplex, asynchronous mode, TDM masks, mono handling, dual FIFO and dynamic FIFO DMA, FIQ stream filter boards, AC97 codec register read/write and playback/capture, suspend/resume preserving SFCSR/SACNT, old DT legacy card creation, debugfs `stats`, and interrupt counters for underrun/overrun/frame events.
