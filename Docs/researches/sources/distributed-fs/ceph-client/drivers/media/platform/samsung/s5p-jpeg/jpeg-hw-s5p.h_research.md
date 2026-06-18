# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.h

Purpose: public declarations and limits for the original S5P JPEG register backend.

Important APIs and constants: defines min/max dimensions, raw input/output mode ids, and declarations for reset, power, mode/subsampling/restart/table/dimension/interrupt/address/coefficient/start/status/compressed-size helpers.

Control flow role: consumed by `jpeg-core.c` for the `SJPEG_S5P` variant and by `jpeg-hw-s5p.c` implementation.

State and persistence: no runtime state; all helpers are stateless operations on a passed MMIO base.

Dependencies and integration: includes `linux/io.h`, `linux/videodev2.h`, and `jpeg-regs.h`. The core uses its constants for legacy S5P format programming.

Risks: declared width/height limits are broad; actual alignment and buffer-size constraints are enforced in the core. Caller must provide valid clocks/register mapping and serialized access.

Test signals: build/prototype checks and legacy variant encode/decode paths that exercise every declaration reachable from `s5p_jpeg_device_run()` and `s5p_jpeg_irq()`.
