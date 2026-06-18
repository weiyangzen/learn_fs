# File Research: sources/block-storage/util-linux/libblkid/Makemodule.am

## Purpose
Top-level Autotools module gate for building libblkid inside util-linux. It conditionally includes the library implementation and sample build fragments when `BUILD_LIBBLKID` is enabled.

## Main Components
- Includes `libblkid/src/Makemodule.am` for the actual library, test, install, and source-list rules.
- Includes `libblkid/samples/Makemodule.am` for sample binaries.
- Adds `libblkid/docs` to `SUBDIRS` only when GTK-Doc is enabled.
- Installs/generates `libblkid/blkid.pc` through `pkgconfig_DATA` and `PATHFILES`.
- Registers `libblkid/libblkid.3` plus its AsciiDoc source and distributes `libblkid/COPYING`.

## Dependencies and Interactions
This file is a thin Autotools coordinator. It relies on project-level conditionals such as `BUILD_LIBBLKID` and `ENABLE_GTK_DOC`, and delegates most details to the included module files.

## Research Notes
The file contains no library logic; its correctness is about build graph inclusion and distribution/install metadata.
