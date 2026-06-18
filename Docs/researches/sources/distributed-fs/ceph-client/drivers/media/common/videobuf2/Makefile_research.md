# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/Makefile

Purpose: Builds the Videobuf2 common object and optional vb2 backend modules based on Kconfig selections. It is the bridge between `CONFIG_VIDEOBUF2_*` symbols and the actual object files under `drivers/media/common/videobuf2/`.

Important APIs, types, and functions: defines `videobuf2-common-objs := videobuf2-core.o`, always adds `frame_vector.o`, conditionally adds `vb2-trace.o` when `CONFIG_TRACEPOINTS=y`, and maps `CONFIG_VIDEOBUF2_CORE`, `DMA_CONTIG`, `DMA_SG`, `DVB`, `MEMOPS`, `V4L2`, and `VMALLOC` to their corresponding objects through `obj-$(CONFIG_...)`.

Control flow: during kbuild, enabling `CONFIG_VIDEOBUF2_CORE` builds `videobuf2-common.o` from the listed component objects. Tracepoints are compiled into the common object only when tracepoint support is built in. Backend symbols build separate objects such as `videobuf2-dma-contig.o`, `videobuf2-dma-sg.o`, `videobuf2-v4l2.o`, and `videobuf2-vmalloc.o`.

State and persistence behavior: no runtime state exists in the Makefile. Its only persistent effect is the generated build graph and object/module composition for a particular kernel configuration.

Dependencies and integration points: consumes the Kconfig symbols from the same directory and `CONFIG_TRACEPOINTS` from the kernel tracing configuration. It integrates `frame_vector.c` into `videobuf2-common.o`, and includes `vb2-trace.c` only when the tracepoint definitions can be created and exported. The alphabetical sort comment is an ordering invariant for maintainability.

Risks and invariants: `vb2-trace.o` must not be compiled without tracepoint support because it defines `CREATE_TRACE_POINTS` for `<trace/events/vb2.h>`. `frame_vector.o` is always part of the core common object, so any dependencies it gains affect all vb2-core users. Reordering is low-risk mechanically but the comment signals maintainers expect Kconfig-name order.

Test signals: run representative media builds with `CONFIG_TRACEPOINTS=y` and disabled, and with each backend as module/built-in. Link tests should confirm `videobuf2-common.o` exports frame-vector helpers and tracepoints only in the intended configurations. Kbuild warnings about missing objects or duplicate tracepoint definitions are high-signal failures.
