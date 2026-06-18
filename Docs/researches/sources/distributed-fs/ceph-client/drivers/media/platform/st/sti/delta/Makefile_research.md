# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Makefile

Purpose: maps Delta Kconfig selections to the `st-delta` module object list.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_DELTA_DRIVER) += st-delta.o` creates the module. Core objects are `delta-v4l2.o`, `delta-mem.o`, `delta-ipc.o`, and `delta-debug.o`. MJPEG support conditionally adds `delta-mjpeg-hdr.o` and `delta-mjpeg-dec.o`.

Control flow: kbuild links the core V4L2, memory, IPC, and debug code into one module, then appends codec-specific objects according to `CONFIG_VIDEO_STI_DELTA_MJPEG`.

State and persistence: no runtime state. It controls compilation units and therefore which decoder registrations are possible at runtime.

Dependencies and integration points: must stay aligned with `Kconfig`, `delta-cfg.h` external decoder declarations, and the `delta_decoders[]` registry in `delta-v4l2.c`.

Risks: adding a decoder requires coordinated updates in Kconfig, this Makefile, and the decoder registry. Missing a core object would leave unresolved internal symbols such as `delta_ipc_open` or `delta_get_frameinfo_default`.

Test signals: `make M=drivers/media/platform/st/sti/delta` with MJPEG enabled validates the build shape; disabling MJPEG should omit MJPEG objects and avoid unresolved `mjpegdec` references.
