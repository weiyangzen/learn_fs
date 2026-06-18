# File Research: sources/block-storage/util-linux/libblkid/meson.build

## Purpose
Meson build definition for libblkid. It configures the public header, defines the library source set, builds shared/static libraries, exports dependencies, generates pkg-config metadata, and builds sample programs.

## Main Components
- Establishes `dir_libblkid = include_directories('.', 'src')`.
- Disables `blkid_dep` and `blkid_static_dep` and exits early when `build_libblkid` is false.
- Generates `blkid.h` from `src/blkid.h.in` with date/version substitutions.
- Defines `lib_blkid_sources`, covering core cache/probe/evaluation modules, partition probers, superblock probers, and topology modules.
- Adds Linux-only topology backends when `LINUX` is true.
- Applies `src/libblkid.sym` as a linker version script if supported.
- Builds `both_libraries('blkid', ...)`, linking against `lib_common` and conditionally `lib_econf`.
- Declares Meson dependencies for shared and static consumers and overrides dependency name `blkid` on Meson >= 0.54.0.
- Generates pkg-config metadata.
- Builds sample programs `sample-mkfs`, `sample-partitions`, `sample-superblocks`, and `sample-topology`.

## Dependencies and Interactions
This file mirrors the Autotools source inventory from `src/Makemodule.am`. It depends on global Meson variables such as `build_libblkid`, `pc_version`, `libblkid_version`, `lib_common`, `lib_econf`, `list_h`, `dir_include`, and platform feature variables.

## Research Notes
The Meson file is authoritative for Meson consumers and includes the same partition files researched in this group. It explicitly fails when neither `dirfd` nor `ddfd` is available, because libblkid internals require directory file-descriptor support.
