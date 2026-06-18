# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-hw.c

Purpose: contains the low-level register programming helpers for the STM32 DMA2D/Chrom-Art V4L2 mem2mem driver. It translates `struct dma2d_frame` and operation mode state into DMA2D hardware register writes.

Important APIs: `dma2d_start` sets `CR_START`; `dma2d_get_int` reads interrupt status; `dma2d_clear_int` acknowledges all currently set interrupt flags; `dma2d_config_common` programs operation mode and output dimensions; `dma2d_config_out` enables interrupts, programs output pixel format, destination address, output color, and output line offset; `dma2d_config_fg` and `dma2d_config_bg` program foreground/background memory addresses, offsets, input pixel formats, alpha modes, alpha values, and default colors.

Control flow: `dma2d.c` calls these helpers from `device_run` after selecting source and destination vb2 buffers. Foreground is configured from the output/source queue buffer, destination is configured from the capture buffer, common mode/size is written, and `dma2d_start` launches the transfer. Completion is handled by the parent driver's IRQ path.

State and persistence: state is hardware MMIO register state only, plus the caller-owned `dma2d_dev` and frame structures. There is no persistent storage. Register access uses relaxed reads/writes, so ordering expectations rely on device semantics and caller locking.

Dependencies and risks: depends on `dma2d.h`, `dma2d-regs.h`, Linux IO accessors, and valid DMA addresses from vb2 DMA-contig. Risks include incorrect bitfield masking for alpha mode (`(a_mode << 16) & 0x03` appears narrower than the shifted field), unsupported color mode values being silently ignored, interrupt enable policy being embedded in output config, and no explicit memory barriers around start. Test signals are register traces, RGB format conversion tests, R2M fill color tests, interrupt status/clear behavior, and comparing output pixels for every advertised format.
