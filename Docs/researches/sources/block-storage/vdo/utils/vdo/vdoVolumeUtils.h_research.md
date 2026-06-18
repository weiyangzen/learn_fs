# File Research: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.h

## Purpose

`vdoVolumeUtils.h` declares shared loading/freeing helpers for `UserVDO` instances backed by a file or block device.

## API

Declared functions:

- `makeVDOFromFile(const char *filename, bool readOnly, UserVDO **vdoPtr)`
- `readVDOWithoutValidation(const char *filename, UserVDO **vdoPtr)`
- `freeVDOFromFile(UserVDO **vdoPtr)`

The loader functions are annotated with `__must_check`, requiring callers to handle error status codes.

## Dependencies

Includes:

- `types.h`
- `userVDO.h`

## Design Notes

The header intentionally hides the internal `PhysicalLayer` construction details. Callers only need a filename, a read-only flag where applicable, and a `UserVDO **` result slot.

This file is the public boundary for `vdoVolumeUtils.c`.
