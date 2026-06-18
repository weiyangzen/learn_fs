# File Research: sources/block-storage/lvm2/lib/Makefile.in

## Role

This makefile defines the source list for `liblvm-internal.a`, the internal LVM2 library used by command and daemon code. It is the build aggregation point for metadata, devices, filters, reporting, segment types, and activation support.

## Build Behavior

- Always includes `activate/activate.c`, so the high-level activation API is compiled even when devmapper support is disabled. In that case `activate.c` provides stub implementations for many activation functions.
- Adds `activate/dev_manager.c` and `activate/fs.c` only when `@DEVMAPPER@` is `yes`; these are the real device-mapper backend and fallback `/dev/<vg>/<lv>` symlink implementation.
- Adds `lvmpolld/lvmpolld-client.c`, `locking/lvmlockd.c`, and `vdo/vdo.c` behind configure flags.
- Sets `LIB_NAME = liblvm-internal`, `LIB_STATIC = $(LIB_NAME).a`, and uses the shared LVM build template via `include $(top_builddir)/make.tmpl`.
- Populates `CFLOW_LIST` from `SOURCES`, enabling cflow dependency generation for the internal library.

## Dependency Context

The activation files in this group are part of the same static library as metadata manipulation, device discovery, filters, segment-type modules, locking, memory locking, reporting, and misc helpers. This explains the dense internal include graph in `activate.c` and `dev_manager.c`: activation is not an isolated frontend; it consumes committed/precommitted LV metadata and writes device-mapper tables from that metadata.

## Important Invariants

- `activate/activate.c` must remain unconditional because public activation APIs need linkable stubs without devmapper.
- `activate/dev_manager.c` and `activate/fs.c` must remain conditional on devmapper because they directly use libdevmapper task/tree and udev-cookie operations.
- Any new segment type that needs activation normally requires both a source entry elsewhere in this makefile and activation hooks through segment-type ops consumed by `dev_manager.c`.
