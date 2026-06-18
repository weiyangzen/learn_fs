<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c

## Purpose
Implements emulated double-precision floating load from user memory.

## Important APIs, types, and functions
`int lfd(void *frD, void *ea)` calls `copy_from_user(frD, ea, sizeof(double))`.

## Control flow
The function copies eight bytes from the effective address into the destination FPR image or returns `-EFAULT`.

## State and persistence behavior
Destination FPR image is updated on success; no FPSCR state changes.

## Dependencies and integration points
Used by `do_mathemu` for D-form and X-form `lfd` instructions.

## Risks and edge cases
It relies on caller-computed effective addresses and uaccess fault handling; endian representation is raw memory order.

## Test signals
Correct FPR bytes after load and `-EFAULT` on inaccessible user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c -->
