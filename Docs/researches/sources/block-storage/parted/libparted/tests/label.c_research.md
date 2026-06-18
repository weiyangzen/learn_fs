# File Research: sources/block-storage/parted/libparted/tests/label.c

## Purpose

`label.c` provides generic create/probe/read/clone tests for implemented libparted disk-label backends.

## Main Responsibilities

- Creates an 80 MiB temporary disk image for each test case.
- Iterates all registered disk types via `ped_disk_type_get_next()`.
- Skips labels rejected by `_implemented_disk_label()`.
- Tests fresh label creation and commit.
- Tests probing the just-created label.
- Tests reading the just-created label with `ped_disk_new()`.
- Tests duplicating the just-created in-memory label.

## Test Cases

- `test_create_label`
- `test_probe_label`
- `test_read_label`
- `test_clone_label`

## Notable Details

The test prints each label name to stderr as it runs. It checks that probing and reading return the same disk type name as the one created. Skipped types include Amiga, AIX, PC-98, and Atari on non-512-byte sectors.
