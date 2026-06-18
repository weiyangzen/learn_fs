# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun4i-spdif.c

## Purpose
`sun4i-spdif.c` implements the Allwinner S/PDIF transmit CPU DAI. It programs S/PDIF TX format, IEC958 channel status, clocks, FIFO/DMA controls, runtime PM, and SoC-specific FIFO/clock/reset differences.

## Important APIs, Types, And Functions
`struct sun4i_spdif_dev` stores platform device, S/PDIF TX clock, APB clock, optional reset, a per-instance DAI-driver copy, regmap, TX DMA parameters, quirks, and a spinlock for IEC958 status registers. `struct sun4i_spdif_quirks` selects TX FIFO offset, reset requirement, TX FIFO flush bit, MCLK multiplier, and optional TX clock name. Main functions include `sun4i_spdif_configure()`, `sun4i_spdif_startup()`, `sun4i_spdif_hw_params()`, `sun4i_spdif_trigger()`, IEC958 control get/put helpers, runtime suspend/resume, and probe/remove.

## Control Flow
Probe allocates state, copies the static DAI driver to set a per-device name, maps registers, loads quirks, initializes regmap, gets APB and S/PDIF/TX clocks, fills TX DMA FIFO address and default width, optionally deasserts reset, registers the component/DAI, enables runtime PM or resumes manually, and registers DMAengine PCM. Startup rejects capture streams and soft-resets/configures the transmitter. `hw_params()` validates one/two-channel PCM or four-channel raw mode, selects 16/20/24-bit S/PDIF formatting and DMA width, chooses the clock family for the requested sample rate, applies the SoC MCLK multiplier, sets the TX clock rate, computes the hardware TX ratio, and writes TX configuration including channel-status mode. Trigger start enables single-channel mode if needed, TX, TX DRQ, and global enable; trigger stop disables them. IEC958 controls read/write channel-status registers under the spinlock and set the non-audio TX bit from status byte 0.

## State And Persistence
The driver persists TX configuration, channel-status registers, clock enable state, DMA parameters, runtime PM state, and optional reset state. The channel-status control state lives directly in hardware registers rather than a separate software cache.

## Dependencies And Integration Points
The driver binds A10, A31, H3, H6, H616, and A523 S/PDIF compatibles. It depends on MMIO regmap, `apb` and `spdif` or variant `tx` clocks, optional reset control, DMAengine PCM, ASoC DAI/component APIs, ALSA IEC958 controls, and machine drivers that connect the playback-only DAI.

## Risks And Edge Cases
Although RX registers and bits are defined, the DAI and startup path are playback-only. Rate support is limited to explicit 22.05/44.1/88.2/176.4 and 24/32/48/96/192 kHz families; 8/11.025/16 kHz are advertised via `SNDRV_PCM_RATE_8000_192000` but rejected by `hw_params()`, which is an important contract mismatch to test. Mono mode is only set on start and is not explicitly cleared for later stereo streams unless TXCFG is rewritten by `hw_params()`. H3 multiplies MCLK by four and A523 uses a different TX clock name, so clock-tree regressions are easy to introduce.

## Test Signals
Validate probe for every compatible, missing clocks/reset failures, runtime PM resume/suspend clock balance, S16_LE/S20_3LE/S24_LE/S32_LE playback, one/two/four-channel behavior, accepted and rejected sample rates, IEC958 mask/default get/put and non-audio bit updates, FIFO flush and TX counter clear on startup, trigger enable/disable bits, and DMA address selection for old versus sun8i TX FIFO offsets.
