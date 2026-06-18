# File Research: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.c

## Purpose

`vdoVolumeUtils.c` provides common helper routines for loading and freeing a `UserVDO` from a file or block device. Many utilities in this directory use these wrappers instead of directly constructing a `PhysicalLayer` and loading VDO metadata.

## Main API

Public functions:

- `makeVDOFromFile(const char *filename, bool readOnly, UserVDO **vdoPtr)`
- `readVDOWithoutValidation(const char *filename, UserVDO **vdoPtr)`
- `freeVDOFromFile(UserVDO **vdoPtr)`

Internal helper:

- `loadVDOFromFile(const char *filename, bool readOnly, bool validateConfig, UserVDO **vdoPtr)`

## Behavior

`loadVDOFromFile()` enforces:

```c
validateConfig || readOnly
```

This prevents creating a writable VDO layer without validating config.

It then:

1. Builds either a read-only or writable `PhysicalLayer`:
   - `makeReadOnlyFileLayer(filename, &layer)`
   - `makeFileLayer(filename, 0, &layer)`
2. Calls `loadVDO(layer, validateConfig, &vdo)`.
3. On load failure, destroys the layer and reports the decoded VDO error with `warnx()`.
4. On success, returns the `UserVDO`.

`freeVDOFromFile()`:

1. Handles `NULL` input gracefully.
2. Saves `vdo->layer`.
3. Calls `freeUserVDO(&vdo)`.
4. Destroys the physical layer.
5. Clears the caller’s pointer.

## Dependencies

Includes:

- `vdoVolumeUtils.h`
- `err.h`
- `errors.h`
- `permassert.h`
- `status-codes.h`
- `fileLayer.h`
- `userVDO.h`

## Used By

This helper is used by VDO metadata and admin utilities including:

- `vdoaudit.c`
- `vdodumpblockmap.c`
- `vdodumpmetadata.c`
- `vdolistmetadata.c`
- `vdostats` indirectly does not load backing files, but other VDO tools use the pattern.
- `vdoreadonly.c` and `vdoforcerebuild.c` use lower-level file layer calls because they mutate metadata states directly.

## Notable Behaviors and Risks

- The static `errBuf` is shared inside this compilation unit only.
- The layer ownership contract is clear: on successful load, the returned `UserVDO` owns a layer that must be released through `freeVDOFromFile()`.
- `readVDOWithoutValidation()` is intentionally read-only and used for metadata inspection paths where config validation may fail or be unnecessary.
