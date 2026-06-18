# File Research: sources/block-storage/parted/libparted/tests/t2000-disk.sh

## Purpose

`t2000-disk.sh` is the shell wrapper for the `disk` Check test binary.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `disk`.
- Exits through the shared `Exit` helper.

## Notable Details

Like the label wrapper, comments mention selecting a directory that supports `O_DIRECT`.
