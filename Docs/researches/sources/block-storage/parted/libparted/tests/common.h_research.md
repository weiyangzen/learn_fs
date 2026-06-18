# File Research: sources/block-storage/parted/libparted/tests/common.h

## Purpose

`common.h` declares shared helpers used by the libparted test programs.

## Contents

- `get_sector_size()`
- `_create_disk()`
- `_create_disk_label()`
- `_implemented_disk_label()`
- `_test_exception_handler()`

## Dependencies and Role

The header includes `<parted/parted.h>` and gives all tests a common way to create disk image fixtures, create labels, filter unsupported labels, and fail on unexpected libparted exceptions.
