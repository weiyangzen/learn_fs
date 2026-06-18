<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S

## Purpose
Provides SPARC64 ASI-aware byte-wise integer load/store helpers for kernel unaligned-access emulation.

## Important APIs, Types, And Functions
Exports `__do_int_store` and `do_int_load`. Both save and restore `%asi`, accept an ASI selected by `unaligned_64.c`, and use `__retl_efault` exception fixups for failing byte accesses.

## Control Flow
`__do_int_store` switches to the requested ASI, splits a 64-bit source value into bytes, and stores 2, 4, or 8 bytes. `do_int_load` switches ASI, loads bytes with `lduba`, assembles 2-, 4-, 8-, or 16-byte logical results, applies signed extension for halfword/word loads, and writes destination register slots. Exception-table entries for every faultable byte load/store return `-EFAULT` after restoring normal control.

## State And Persistence
No durable state is kept. The routine temporarily changes `%asi`, restores it before return, and emits `__ex_table` metadata. Destination memory/register slots are the intended side effects.

## Dependencies And Integration Points
Called from `unaligned_64.c` for kernel integer unaligned emulation and no-fault load handling. It depends on ASI definitions, SPARC64 register ABI, and exception-table code.

## Risks And Edge Cases
Incorrect ASI restore would corrupt later kernel accesses. Little-endian alternate ASIs are normalized by the C caller, so helper byte order assumptions must stay aligned with that caller. The 16-byte case represents ldd/std register-pair semantics and must match the caller’s destination layout.

## Test Signals
Signals include SPARC64 kernel unaligned accesses across primary/secondary/no-fault/little-endian ASIs, faulting byte loads/stores that return `-EFAULT`, and regression checks for `%asi` preservation after emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S -->
