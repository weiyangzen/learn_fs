# sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_lookup.h

## Purpose
Defines ORC unwinder lookup-table block sizing and symbols used to accelerate searches through `.orc_unwind`.

## Important APIs, Types, And Functions
Defines `LOOKUP_BLOCK_ORDER` as 8, `LOOKUP_BLOCK_SIZE` as 256, external symbols `orc_lookup[]` and `orc_lookup_end[]`, and lookup address bounds `LOOKUP_START_IP` and `LOOKUP_STOP_IP` when not in linker-script context.

## Control Flow
The ORC unwinder maps an instruction pointer range to a subset of the ORC table through lookup blocks, reducing search cost. The linker script consumes the same constants without C symbols.

## State And Persistence
The lookup table is generated into kernel image data and is immutable at runtime.

## Dependencies And Integration Points
Integrates with ORC table generation, linker scripts, unwinder runtime, and `_stext`/`_etext` kernel text bounds.

## Risks And Edge Cases
Block size must be a power of two and match generator/runtime expectations. Wrong text bounds or table endpoints can make unwinding fail or search out of range.

## Test Signals
ORC unwinder tests, stack traces under interrupts/exceptions, objtool validation, and linker-script builds are useful.
