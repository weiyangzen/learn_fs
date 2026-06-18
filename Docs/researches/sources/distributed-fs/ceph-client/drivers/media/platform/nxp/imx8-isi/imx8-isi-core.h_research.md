# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.h

## Purpose
`imx8-isi-core.h` is the shared internal contract for the i.MX8 ISI driver. It defines limits, defaults, formats, platform data, crossbar, pipe, video, m2m, buffer, gasket, and device structures, and declares the cross-module APIs used by the core, crossbar, hardware, video, pipe, debug, and optional mem2mem implementation files.

## Important APIs, Types, and Functions
Key constants define pad indices, width and height limits, default media bus codes and pixel format, driver names, and the maximum number of planes. `struct mxc_isi_format_info` and `struct mxc_isi_bus_format_info` describe memory and bus formats. `struct mxc_isi_buffer`, `struct mxc_isi_video`, `struct mxc_isi_pipe`, `struct mxc_isi_crossbar`, `struct mxc_isi_m2m`, and `struct mxc_isi_dev` define the driver's major state containers.

Platform abstractions include `enum model`, `struct mxc_isi_plat_data`, `struct mxc_isi_ier_reg`, `struct mxc_isi_set_thd`, and `struct mxc_gasket_ops`. Resource and control APIs include crossbar init/register functions, format lookup helpers, pipe acquire/release/enable/disable functions, video registration and vb2 helpers, optional m2m hooks, low-level channel acquire/chaining/configuration functions, buffer address programming, IRQ helpers, and debugfs init/cleanup.

## Control Flow
The header has no direct control flow, but it defines the call graph boundaries. `imx8-isi-core.c` constructs `struct mxc_isi_dev`, initializes crossbar and pipes, and registers video/m2m paths. Pipe and video code use channel acquisition and hardware functions to configure registers. Crossbar code uses gasket ops and stream routing. Conditional inline stubs make m2m and debugfs calls no-ops when their Kconfig symbols are disabled.

## State and Persistence
The structures in this header describe all persistent in-kernel runtime state for the ISI driver. Buffer queues and frame counters live in `struct mxc_isi_video`; resource ownership and channel chaining state live in `struct mxc_isi_pipe`; async media topology and platform capabilities live in `struct mxc_isi_dev`. None of the state is persistent across driver unload or system power loss.

## Dependencies and Integration Points
The header depends on Linux list, mutex, spinlock, V4L2, media controller, async notifier, controls, and videobuf2 types. It is included by all ISI implementation files. It also exposes `mxc_imx8_gasket_ops` and `mxc_imx93_gasket_ops` from the gasket implementation.

## Risks and Edge Cases
Because this header is the internal ABI between multiple objects, field-order or semantic changes can break resource ownership, locking, or buffer handling across modules. The `mxc_isi_pipe.lock` protects a broad set of fields and the channel control register; callers must respect that boundary. Conditional m2m/debug stubs must match the real functions' signatures. The `MXC_ISI_MAX_WIDTH_UNCHAINED` and chained resource fields encode the requirement that wider frames consume resources from an adjacent channel.

## Test Signals
Build coverage across all Kconfig combinations is essential. Runtime signals include correct resource acquisition/release across capture and m2m, correct line-buffer chaining above 2048 pixels, no races in video buffer queues under `buf_lock`, valid format enumeration and try-format results from shared helpers, and correct no-op behavior when debugfs or m2m support is disabled.
