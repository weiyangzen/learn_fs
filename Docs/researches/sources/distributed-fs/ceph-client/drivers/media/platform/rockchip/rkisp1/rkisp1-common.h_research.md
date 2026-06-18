# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.h

Purpose: central header for RKISP1 types, feature flags, constants, inline register accessors, and internal function declarations.

Important APIs/types/functions: defines driver names, dimensions, IRQ lines, pad enums, stream IDs, Bayer patterns, feature bits and `rkisp1_has_feature()`, `struct rkisp1_info`, async sensor metadata, CSI/ISP/capture/stats/params/resizer/debug/device structs, `struct rkisp1_mbus_info`, `rkisp1_write()`, `rkisp1_read()`, format/crop helpers, params hooks, IRQ handlers, and entity registration prototypes. `struct rkisp1_device` aggregates platform resources, media/v4l2 devices, notifier, subdevs, video nodes, media pipeline, stream lock, debug counters, match info, IRQs, and IRQ enable state.

Control flow: every RKISP1 module includes this header. Platform probe fills `rkisp1_device` and `rkisp1_info`; entity modules register subdevices/video nodes; IRQ handlers and stream callbacks share the same device and per-entity state.

State and persistence: defines all long-lived in-kernel state for the driver: clocks, PM domains, gasket, active source, CSI source, ISP frame sequencing, capture current/next buffers, metadata queues, debug counters, pipeline lock, and IRQ state. No disk persistence.

Dependencies/integration: includes kernel clock/interrupt/mutex/config headers and V4L2/media/vb2 headers, plus `rkisp1-regs.h`. It is the internal ABI for objects linked into `rockchip-isp1.o`.

Risks: because this is a wide shared header, changes can affect all module boundaries. Feature flags must remain consistent with match data in `rkisp1-dev.c`; wrong flags enable unsupported register paths. State fields used from IRQ and process contexts require the locking discipline documented in each struct comment.

Test signals: full module compile, sparse/lockdep review for lock comments, probe on all match-data variants, runtime stream tests for devices with and without selfpath/MIPI/MAIN_STRIDE/DMA_34BIT, and debugfs counter sanity.
