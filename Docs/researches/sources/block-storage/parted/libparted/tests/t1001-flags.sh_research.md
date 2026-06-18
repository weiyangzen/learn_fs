# File Research: sources/block-storage/parted/libparted/tests/t1001-flags.sh

## Purpose

`t1001-flags.sh` is the shell wrapper for the partition flags unit test.

## Main Responsibilities

- Sources `tests/init.sh`.
- Prepends the current directory to `PATH`.
- Runs `flags`.
- Exits through the shared `Exit` helper.

## Behavior

This wrapper has no special privilege or device setup requirements; it delegates all test logic to `flags.c`.
