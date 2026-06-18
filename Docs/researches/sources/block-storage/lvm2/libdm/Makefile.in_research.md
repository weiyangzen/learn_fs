# File Research: sources/block-storage/lvm2/libdm/Makefile.in

## Purpose
Builds and installs the `libdevmapper` library and its exported header/pkg-config metadata.

## Main Responsibilities
- Defines libdm source files, including datastruct, config, deptree, stats, regex, vdo parser/status/stats, pool allocator, and interface-specific ioctl code.
- Builds static and/or shared `libdevmapper` based on configure substitutions.
- Creates compatibility symlinks for shared library names.
- Runs a symbol-version sanity check for `dm_stats_create_region`.
- Installs headers, shared library, static library, and `devmapper.pc`.

## Key Build Variables
- `SUBDIRS=dm-tools`
- `SOURCES` lists all libdm compilation units.
- `LIB_STATIC`, `LIB_SHARED`, `LIB_VERSION`, and `TARGETS` are gated by `@STATIC_LINK@` and `@SHARED_LINK@`.
- `EXPORTED_HEADER=libdevmapper.h`
- `EXPORTED_FN_PREFIX=dm`

## Install Behavior
- `install` expands to dynamic/static/pkg-config install targets as configured, plus header install.
- `install_ioctl` installs the shared library when shared builds are enabled and static library when static builds are enabled.
- `DISTCLEAN_TARGETS` includes generated `libdevmapper.pc` and `make.tmpl`.
