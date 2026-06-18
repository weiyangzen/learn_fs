# sources/distributed-fs/ceph-client/drivers/block/drbd/Makefile

## Purpose

This Makefile defines how the DRBD kernel object is composed. It aggregates DRBD source objects into `drbd.o`, conditionally includes debugfs support, and links the final object according to `CONFIG_BLK_DEV_DRBD`.

## Important Build Rules

- `drbd-y` includes core objects: `drbd_buildtag.o`, `drbd_bitmap.o`, `drbd_proc.o`, `drbd_worker.o`, `drbd_receiver.o`, `drbd_req.o`, `drbd_actlog.o`, `drbd_main.o`, `drbd_strings.o`, `drbd_nl.o`, `drbd_interval.o`, and `drbd_state.o`.
- `drbd-$(CONFIG_DEBUG_FS) += drbd_debugfs.o` includes debugfs instrumentation only when debugfs is configured.
- `obj-$(CONFIG_BLK_DEV_DRBD) += drbd.o` builds DRBD according to the tristate selected in Kconfig.

## Control Flow and Integration

There is no runtime control flow. The file controls object composition. The ordering places build tag and bitmap/proc objects first, followed by worker, receiver, request, activity-log, main, strings, netlink, interval, and state components. Debugfs is compile-time optional while the header provides stubs for non-debugfs builds.

## State and Persistence Behavior

No runtime state is stored here. Build selection affects which runtime code paths are present.

## Dependencies

- Consumes `CONFIG_BLK_DEV_DRBD` from `Kconfig`.
- Consumes `CONFIG_DEBUG_FS` from the broader kernel config.
- Assumes all listed DRBD source files participate in one module/built-in object.

## Risks and Edge Cases

- Adding a new DRBD translation unit requires updating `drbd-y`; missing objects can surface as unresolved symbols or disabled functionality.
- Debugfs code must remain optional and all callers must tolerate stubbed debugfs functions when `CONFIG_DEBUG_FS=n`.
- Build tag logic depends on `drbd_buildtag.o` always being present.

## Test Signals

- Build with `CONFIG_BLK_DEV_DRBD=n/m/y`.
- Build with `CONFIG_DEBUG_FS=n/y` and confirm `drbd_debugfs.o` is included only with debugfs.
- Module build should expose a coherent `drbd.ko` with all required symbols resolved.
