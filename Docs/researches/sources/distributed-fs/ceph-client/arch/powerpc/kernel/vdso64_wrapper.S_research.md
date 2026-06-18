# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso64_wrapper.S

## Purpose
Embeds the built 64-bit PowerPC vDSO shared object into the kernel image.

## Important APIs, Types, And Functions
Defines `vdso64_start` and `vdso64_end` in `.data..ro_after_init`, page-aligns both boundaries, and includes `arch/powerpc/kernel/vdso/vdso64.so.dbg`.

## Control Flow
The assembler includes the linked vDSO image into kernel data. `vdso.c` later converts the embedded range into pages for special mappings.

## State And Persistence
The embedded vDSO image is static kernel data that becomes read-only after init.

## Dependencies And Integration Points
Depends on `vdso64.so.dbg` build output, `PAGE_SIZE`, and runtime references from `vdso.c`.

## Risks And Edge Cases
Missing or stale included vDSO artifacts break the kernel build or map an outdated ABI image. Page alignment must be preserved for page-list mapping.

## Test Signals
Build tests for 64-bit PowerPC, symbol inspection for `vdso64_start/end`, and runtime vDSO function tests validate the wrapper.
