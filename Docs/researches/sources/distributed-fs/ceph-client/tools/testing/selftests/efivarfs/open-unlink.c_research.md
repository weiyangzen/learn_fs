# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/open-unlink.c

## Purpose
Helper that verifies reading from an efivarfs variable after unlink through an already-open fd does not return data.

## Important APIs, Types, And Functions
Local helpers `set_immutable()` and `get_immutable()` use `FS_IOC_GETFLAGS` and `FS_IOC_SETFLAGS` to clear `FS_IMMUTABLE_FL`. `main()` uses `open`, `write`, `unlink`, `read`, and EFI attribute bytes.

## Control Flow
It creates a variable with attributes plus one byte of data, clears immutable if set, opens it read-only, unlinks it, then reads from the still-open fd. Returning positive bytes is a failure.

## State And Persistence
Creates and removes one efivarfs variable path supplied by the shell script. It mutates immutable flags for cleanup.

## Dependencies And Integration Points
Called by `efivarfs.sh` `test_open_unlink()`. Requires Linux fs ioctl support and efivarfs behavior.

## Risks
The code writes a `uint32_t` directly into a `char` buffer, relying on alignment tolerated by target architectures. If unlink fails, the variable may remain until caller cleanup.

## Test Signals
Success is variable creation, immutable clearing as needed, successful unlink, and non-positive read after unlink.
