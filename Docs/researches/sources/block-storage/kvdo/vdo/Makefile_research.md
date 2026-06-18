# File Research: sources/block-storage/kvdo/vdo/Makefile

## Purpose

Kbuild makefile for building the `kvdo` kernel module from all C sources in the `vdo` directory.

## Main Responsibilities

- Defines `VDO_VERSION = 8.2.7.4`.
- Discovers local C files with `$(wildcard $(src)/*.c)` and maps them to object files.
- Adds `-I$(src)` include path.
- Derives `RHEL_RELEASE_EXTRA` from `uname -r` unless supplied externally.
- Sets module compiler flags:
  - GNU11 mode,
  - no builtin `memset`,
  - `-Werror`,
  - optional stack-frame limit when KASAN is disabled,
  - `CURRENT_VERSION`,
  - `RHEL_RELEASE_EXTRA`.
- Builds `kvdo.o` as `obj-m` from all discovered objects.

## Notable Details

Every `.c` file in this directory becomes part of `kvdo-objs`, so adding a C file automatically links it into the module.
