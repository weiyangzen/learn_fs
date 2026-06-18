# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso32_wrapper.S

## Purpose
Embeds the built 32-bit PowerPC vDSO shared object into the kernel image.

## Important APIs, Types, And Functions
Defines global symbols `vdso32_start` and `vdso32_end` in `.data..ro_after_init`, aligned to `PAGE_SIZE`, and includes `arch/powerpc/kernel/vdso/vdso32.so.dbg` with `.incbin`.

## Control Flow
At assembly/link time the vDSO binary is copied byte-for-byte into the kernel. Runtime code in `vdso.c` uses the start/end symbols to create page lists and map the image into userspace.

## State And Persistence
The embedded bytes become read-only-after-init kernel data. There is no active control flow in this file.

## Dependencies And Integration Points
Depends on the vDSO Makefile producing `vdso32.so.dbg`, page alignment, and `vdso.c` external symbol declarations.

## Risks And Edge Cases
The included file path must match the object tree layout. Incorrect alignment or missing end padding would break page-list construction and mapping size calculations.

## Test Signals
Build tests with `CONFIG_VDSO32`, symbol inspection for `vdso32_start/end`, and runtime 32-bit vDSO mapping tests validate this wrapper.
