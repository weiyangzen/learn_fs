<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/Makefile -->
# sources/distributed-fs/ceph-client/fs/iomap/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/Makefile` defines the build composition of the generic iomap library. It builds the `iomap.o` composite object when `CONFIG_FS_IOMAP` is enabled and conditionally includes block and swap support pieces.

## Important APIs, Types, and Functions

The build variables are `ccflags-y`, `obj-$(CONFIG_FS_IOMAP)`, `iomap-y`, `iomap-$(CONFIG_BLOCK)`, and `iomap-$(CONFIG_SWAP)`. Core objects are `trace.o`, `iter.o`, and `buffered-io.o`; block-enabled objects are `direct-io.o`, `ioend.o`, `fiemap.o`, `seek.o`, and `bio.o`; swap support adds `swapfile.o`.

## Control Flow

Kbuild adds `-I $(src)` so trace event headers in the iomap directory can be included. If `CONFIG_FS_IOMAP` is enabled, Kbuild links `iomap.o`. The base object list always includes tracing, iteration, and buffered I/O. Extra objects are included only when their configuration symbols are enabled.

## State and Persistence Behavior

The file has no runtime state. Its build-time state determines which iomap capabilities are present in the resulting kernel.

## Dependencies and Integration Points

It integrates the iomap library with kernel configuration. Filesystems that use iomap depend on this object composition for exported buffered write/read helpers, iterator support, tracepoints, direct I/O, fiemap/seek, bio read support, and swapfile helpers.

## Risks and Edge Cases

Misplacing an object in the wrong conditional can create link failures or missing exported symbols. `buffered-io.o` is part of the base iomap library, while `bio.o` is gated by `CONFIG_BLOCK`; callers must only use block-backed bio read ops when block support exists. Trace include paths must remain correct for generated trace headers.

## Test Signals

Build matrices should cover `CONFIG_FS_IOMAP=y/m/n`, `CONFIG_BLOCK=y/n` where applicable, and `CONFIG_SWAP=y/n`. Link failures in iomap exports or missing trace definitions are the main regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/Makefile -->
