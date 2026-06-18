# File Research: sources/block-storage/parted/libparted/tests/t3000-symlink.sh

## Purpose

`t3000-symlink.sh` is the privileged shell wrapper for the `/dev/mapper` symlink test.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Sources `tests/t-lib-helpers.sh`.
- Requires root privileges.
- Runs the `symlink` test binary.
- Exits through the shared `Exit` helper.

## Behavior Under Test

The wrapper provides the root context required for `symlink.c` to create and retarget a symlink under `/dev/mapper`.
