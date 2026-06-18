# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.h

Purpose: this header defines the core data model and callback contracts for the Meson VDEC driver. It is shared by the platform core, ESPARSER, hardware back ends, helpers, and codec implementations.

Important APIs and types: `struct amvdec_core` stores singleton device resources: MMIO bases, AO regmap, clocks, reset, canvas provider, V4L2/video devices, current session, platform data, and lock. `struct amvdec_ops` abstracts hardware block operations: start, stop, parser config, and VIFIFO level. `struct amvdec_codec_ops` abstracts codec operations including start/stop, optional extended firmware, pending buffer accounting, recycle, drain, resume, EOS sequence, and ISR callbacks. `struct amvdec_format` maps a coded OUTPUT pixel format to buffer limits, resolution limits, flags, hardware ops, codec ops, firmware path, and supported capture formats. `struct amvdec_session` is the per-open decode state. `amvdec_get_output_size()` is declared for shared output sizing.

Control flow and integration: platform tables bind formats to a pair of hardware and codec ops. `vdec.c` uses `amvdec_session` for all queue, format, event, and streaming state, while codec files attach private data through `priv` and use helper functions to complete buffers or signal source changes.

State and persistence behavior: the header documents all persistent per-device and per-session fields: stream flags, sequence counters, VIFIFO memory, canvas allocations, timestamp/recycle lists, active status, format fields, pixel aspect, and firmware buffer-index mapping. This makes it the main ownership map for cleanup paths.

Dependencies: includes Linux IRQ, regmap, list, V4L2/vb2, controls, V4L2 device, Meson canvas, and `vdec_platform.h`.

Risks: many fields are accessed across workqueue, IRQ, threaded IRQ, recycle kthread, and ioctl contexts, so locking expectations must stay clear. Optional codec callbacks require null checks in generic code. `fw_idx_to_vb2_idx[32]` bounds firmware buffer indices and should align with format max buffer counts.

Test signals: compile coverage across every implementation file after struct changes; runtime stress around queueing, IRQ completion, recycle thread, source changes, and streamoff validates the documented ownership model.
