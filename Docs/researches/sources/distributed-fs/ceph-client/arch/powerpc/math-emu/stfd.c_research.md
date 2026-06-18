<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c

## Purpose
Implements emulated double-precision floating store to user memory.

## Important APIs, types, and functions
`int stfd(void *frS, void *ea)` calls `copy_to_user(ea, frS, sizeof(double))`.

## Control flow
It copies eight bytes from the source FPR image to the effective user address or returns `-EFAULT`.

## State and persistence behavior
Mutates user memory on success; no FPSCR state changes.

## Dependencies and integration points
Dispatched for `STFD`, `STFDU`, `STFDX`, and `STFDUX`.

## Risks and edge cases
Fault handling and update-form base register writes are handled by `math.c`; raw endian memory representation is preserved.

## Test signals
Correct user memory bytes and `-EFAULT` on invalid destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c -->
