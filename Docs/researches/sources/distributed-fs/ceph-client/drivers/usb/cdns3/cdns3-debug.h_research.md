# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-debug.h

Purpose: Provides inline debug formatting helpers for CDNS3 USB and endpoint interrupts and for dumping endpoint TRB rings.

Important APIs, types, and functions: `cdns3_decode_usb_irq` appends human-readable USB interrupt names and speed. `cdns3_decode_ep_irq`, `cdns3_decode_epx_irq`, and `cdns3_decode_ep0_irq` decode endpoint status bits. `cdns3_dbg_ring` formats dequeue/enqueue indexes, DMA/virtual addresses, free TRB counts, cycle states, and each TRB's buffer/length/control values.

Control flow: Each helper writes formatted text into a caller-provided buffer using `sprintf` and returns the same buffer. `cdns3_dbg_ring` derives ring length from endpoint type through `GET_TRBS_PER_SEGMENT`, stops with a warning if the derived count exceeds `TRBS_PER_SEGMENT`, then walks the ring linearly.

State and persistence behavior: No persistent state; it reads endpoint fields and TRB memory for diagnostics.

Dependencies and integration points: Includes `core.h` and uses CDNS3 register/status macros, `usb_speed_string`, TRB helpers, and `struct cdns3_endpoint`. Intended for debugfs, trace, or dev_dbg-style consumers.

Risks: The functions assume the destination buffer is large enough; there is no bounds checking. Because they read live ring state without taking locks themselves, callers must ensure stable endpoint state if exact dumps matter. `sprintf(str + ret, ...)` patterns can overrun if used with small stack buffers.

Test signals: Compile with debug/trace users, exercise endpoint interrupt formatting for each bit, dump rings for bulk/control/isoc endpoints, and run with lockdep/KASAN to catch misuse around buffer sizing or stale endpoint pointers.
