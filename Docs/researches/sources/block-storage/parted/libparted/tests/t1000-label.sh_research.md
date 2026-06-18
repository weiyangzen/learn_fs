# File Research: sources/block-storage/parted/libparted/tests/t1000-label.sh

## Purpose

`t1000-label.sh` is the shell wrapper for the `label` Check test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `label`.
- Exits through the shared `Exit` helper with accumulated failure status.

## Notable Details

The comments say the wrapper is used to find a directory supporting `O_DIRECT`, inherited from the broader test harness behavior.
