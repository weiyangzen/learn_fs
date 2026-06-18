# File Research: sources/block-storage/parted/libparted/tests/t4000-volser.sh

## Purpose

`t4000-volser.sh` is the shell wrapper for the S390 VOLSER/VTOC test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `volser`.
- Exits through the shared `Exit` helper.

## Notable Details

The C test itself compiles meaningful tests only on `__s390__` or `__s390x__`; on other architectures it returns success without running VTOC checks.
