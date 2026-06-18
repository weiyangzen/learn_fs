# File Research: sources/block-storage/parted/libparted/tests/Makefile.am

## Purpose

`Makefile.am` defines the libparted unit test binaries and shell test wrappers.

## Main Responsibilities

- Declares shell tests:
  - `t1000-label.sh`
  - `t1001-flags.sh`
  - `t2000-disk.sh`
  - `t2100-zerolen.sh`
  - `t3000-symlink.sh`
  - `t4000-volser.sh`
- Builds Check-based test programs:
  - `label`
  - `disk`
  - `zerolen`
  - `symlink`
  - `volser`
  - `flags`
- Links tests against `libparted.la`, Check libraries, and pthreads.
- Adds include paths for source/build libparted headers.
- Creates a local `init.sh` symlink before test logs are produced.
- Exports `top_srcdir`, `abs_top_srcdir`, and `ENABLE_DEVICE_MAPPER` to test scripts.

## Dependencies and Interactions

This file connects the C tests in this directory to the broader GNU test harness under `tests/init.sh` and `tests/t-lib-helpers.sh`.
