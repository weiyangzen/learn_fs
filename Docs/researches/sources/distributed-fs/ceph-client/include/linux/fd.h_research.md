# sources/distributed-fs/ceph-client/include/linux/fd.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fd.h` wraps floppy UAPI definitions and adds a compat ioctl payload for 32-bit userspace. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

It includes `uapi/linux/fd.h`. Under `CONFIG_COMPAT`, it defines `struct compat_floppy_struct` and `FDGETPRM32`.

## Control Flow

There is no local flow. Floppy ioctl handling uses the compat structure to translate `FDGETPRM` for 32-bit callers.

## State and Persistence Behavior

No state is owned by the header. Runtime state lives in floppy drive geometry and driver data.

## Dependencies and Integration Points

It integrates with the floppy block driver, ioctl layer, and compat subsystem.

## Risks and Edge Cases

Compat pointer and integer width mismatches can corrupt geometry reporting. The `name` field uses a compat userspace address.

## Test Signals

Compat ioctl build coverage and floppy ioctl translation tests where hardware or emulation is available.
