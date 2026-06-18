# File Research: sources/block-storage/parted/libparted/tests/volser.c

## Purpose

`volser.c` tests DASD VOLSER and VTOC behavior on S390/S390x builds.

## Main Responsibilities

On S390/S390x only:

- Creates a 20 MiB temporary disk image.
- Creates a `dasd` disk label.
- Opens the device and initializes an fdasd anchor.
- Reads DASD geometry and checks the volume.
- Derives the default VOLSER from the device number.
- Tests reading the default VOLSER after writing labels.
- Tests VOLSER normalization:
  - long input is uppercased and truncated,
  - underscore/space case is normalized,
  - blank input falls back to device-number VOLSER.
- Tests changing the VOLSER and reading it back.
- Tests `fdasd_reuse_vtoc()` preserves the first FMT5 free-space extent.

## Dependencies and Interactions

- Includes `<parted/vtoc.h>`, `<parted/fdasd.h>`, and Linux-specific libparted internals.
- Uses the raw file descriptor from `LinuxSpecific`.
- Exercises code paths that depend on `vtoc.c` helpers.

## Notable Details

On non-S390 architectures, `main()` returns success without running any Check suite. The VTOC reuse comparison uses `&&` between field comparisons, so it aborts only if all compared FMT5 extent fields differ.
