# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.h

Purpose: public helper declarations for the Exynos3250-compatible JPEG register backend.

Important APIs: declares reset/power/DMA/clock helpers, raw input/output format setters, Y16 mode, proc mode, subsampling get/set, restart interval, quant/Huffman selector helpers, dimension setters, interrupt/timer helpers, stream bounds, DMA address/stride/offset helpers, coefficient setup, start/restart, compressed size, decode stream size, and decode scaling ratio.

Control flow role: consumed by `jpeg-core.c` when the selected variant uses `exynos3250_jpeg_m2m_ops` and `exynos3250_jpeg_irq()`.

State and persistence: no state; function prototypes operate on a passed MMIO base and immediate values.

Dependencies and integration: includes `linux/io.h`, `linux/videodev2.h`, and `jpeg-regs.h`; depends on `struct s5p_jpeg_addr` from the shared core header through include ordering in users.

Risks: declarations must stay synchronized with the implementation and variant core calls. Because all helpers accept raw register bases, caller locking and PM enablement are external responsibilities.

Test signals: build coverage with `jpeg-core.c`, sparse/prototype checks, and variant-specific smoke tests that touch every declared helper through encode/decode paths.
