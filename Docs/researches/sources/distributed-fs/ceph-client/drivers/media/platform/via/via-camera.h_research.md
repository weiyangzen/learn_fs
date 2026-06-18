# Research: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.h

Purpose: this header is a register map for the VIA capture engines used by the VIA camera platform driver. It has no functions or storage; its API is the set of `VCR_*` offsets and bit masks for interrupt control, transport stream input, capture interface configuration, active/VBI ranges, DMA buffer addresses, stride, and error counters.

Important definitions include `VCR_INTCTRL` status/interrupt bits for EAV, VBI, active buffer, field, FIFO full, and interrupt enables; `VCR_TSC` transport stream enable/drop/count/endianness/serial flags; `VCR_CAPINTC` capture-enable, input format, byte order, deinterlace, filtering, polarity, FIFO threshold, and clock-enable bits; and address/stride registers such as `VCR_VBUF1..3`, `VCR_VBIBUF1..2`, `VCR_VBUF_MASK`, and `VCR_VS_STRIDE`.

Control flow is external: callers include the header and program memory-mapped registers, adding `0x1000` for the second capture engine. State is entirely hardware state persisted in registers and DMA buffer addresses; this file does not cache or synchronize anything. Dependencies are only C preprocessor inclusion and the downstream driver using Linux I/O helpers.

Risks are incorrect bit composition, especially byte-order, CCIR mode, polarity, clock, and buffer-stride fields that directly affect capture corruption or DMA addressing. Test signals are compile success of the VIA camera driver plus hardware tests that verify frame interrupt delivery, buffer selection, stride, VBI buffer handling, and second-engine offset programming.
