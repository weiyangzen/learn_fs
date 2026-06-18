# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.h

Purpose: shared private interface for the Samsung G2D driver. It defines device, context, frame, format, variant structures and prototypes for hardware helper functions.

Important types: `struct g2d_dev` owns V4L2/mem2mem devices, video node, mutex, control spinlock, current context, MMIO registers, clocks, IRQ, and hardware variant. `struct g2d_ctx` is per file handle and stores input/output frames, V4L2 controls, ROP, and flip state. `struct g2d_frame` stores full dimensions, crop dimensions, offsets, format, stride, bottom/right coordinates, and buffer size. `struct g2d_fmt` maps V4L2 fourcc to depth and hardware color mode. `struct g2d_variant` stores hardware revision.

Control flow role: included by `g2d.c` and `g2d-hw.c` so the high-level V4L2 code and low-level register code share the same frame and device layout.

State and persistence: all structures are in-memory runtime state. `dev->curr` bridges mem2mem job submission and IRQ completion.

Dependencies and integration: includes Linux platform and V4L2 device/control headers. Declares hardware helper API consumed by `device_run()` and ISR.

Risks: fields such as `right`, `bottom`, `stride`, and `size` are cached derivatives that must be updated every time formats or selections change. `dev->curr` must be valid exactly while hardware is active.

Test signals: compile coverage, format/selection tests that verify cached fields, concurrent opens/contexts, and IRQ completion validating `dev->curr` lifetime.
