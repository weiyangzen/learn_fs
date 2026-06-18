# File Research: sources/block-storage/parted/parted/Makefile.am

## Purpose

`Makefile.am` defines the build rules for the `parted` frontend binary and its generated version helper library.

## Main Responsibilities

- Builds `sbin_PROGRAMS = parted`.
- Defines frontend sources:
  - `command.c/.h`,
  - `parted.c`,
  - `strlist.c/.h`,
  - `ui.c/.h`,
  - `jsonwrt.c/.h`,
  - `table.c/.h`.
- Builds an internal `libver.a` from generated `version.c` and `version.h`.
- Generates `version.c` with `Version = "$(PACKAGE_VERSION)"`.
- Links `parted` with `libver.a`, `libparted.la`, intl libs, and configured parted libs.
- Adds include paths for source lib, build include, and source include directories.
- Adds linker flags to ignore unused shared-library references.

## Notable Details

Generated version files are chmodded read-only before being moved into place and are removed by `DISTCLEANFILES`.
