# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-regs.h

## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-regs.h

Purpose: Defines the i.MX8 ISI channel register offsets and bitfield macros used by the hardware access layer, video capture path, M2M path, and pipe IRQ handling.

Important APIs/types/functions: This header has no functions; its API is the register contract. Key groups include `CHNL_CTRL` enable/clock/bypass/chain/source fields, `CHNL_IMG_CTRL` output format, alpha, flip, CSC, crop and decimation fields, `CHNL_OUT_BUF_CTRL` load and overflow threshold fields, `CHNL_IER` and `CHNL_STS` interrupt/status bits, scale/crop/CSC coefficient registers, ROI alpha/geometry registers, output/input buffer address and extended address registers, pitch registers, memory-read control fields, and flow-control registers.

Control flow/state: Driver state is persisted in hardware registers addressed by these macros. The capture and M2M paths program image format, input/output DMA addresses, pitch, crop, scale, alpha and flip through helper functions. The pipe IRQ path reads `CHNL_STS` and uses the active-buffer bits to synchronize software queues with hardware ping-pong buffers.

Dependencies/integration: Uses Linux `BIT()` and `GENMASK()` macros. The semantic mapping is consumed by `imx8-isi-hw.c`, `imx8-isi-video.c`, `imx8-isi-m2m.c`, and platform data that describes SoC-specific interrupt masks and panic thresholds.

Risks/test signals: Register macro mistakes are high impact because they silently corrupt hardware configuration. Pay special attention to overlapping fields, extended DMA address handling, active-buffer bit interpretation, and format constants matching `mxc_isi_format_info`. Test by comparing register traces for known capture/M2M formats, validating >32-bit DMA address paths if supported, and checking interrupt/overflow status decoding on hardware.
