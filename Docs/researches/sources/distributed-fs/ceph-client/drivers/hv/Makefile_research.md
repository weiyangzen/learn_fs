# sources/distributed-fs/ceph-client/drivers/hv/Makefile

## Purpose
Maps Hyper-V Kconfig options to composed kernel objects and module build units.

## Important APIs, Types, and Functions
Defines `hv_vmbus-y` from `vmbus_drv.o`, `hv.o`, `connection.o`, `channel.o`, `channel_mgmt.o`, `ring_buffer.o`, and `hv_trace.o`; plus composed objects for utilities, root partition support, and VTL support.

## Control Flow
Kbuild links component objects into modules/built-ins based on configuration. `hv_common.o` is built when `CONFIG_HYPERV` is enabled, and `hv_proc.o`/`mshv_common.o` are conditionally built for MSHV support.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with `drivers/hv/Kconfig`, trace include paths via `CFLAGS_hv_trace.o`, and optional debugfs/tracepoint objects.

## Risks and Test Signals
Risks include missing object membership for exported symbols, incorrect built-in/module split for shared common code, and optional feature link failures. Test signals are successful builds for VMBus-only, utilities, balloon, MSHV root, MSHV VTL, debugfs, and tracepoint configurations.
