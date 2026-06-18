# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/orc_types.h

## Purpose
Defines the compact ORC unwind metadata format used by x86 tooling and the kernel unwinder.

## APIs, Types, and Functions
Exports ORC base-register IDs (`ORC_REG_SP`, `ORC_REG_BP`, `ORC_REG_PREV_SP`, indirect variants), ORC entry types (`ORC_TYPE_CALL`, `ORC_TYPE_REGS`, etc.), and `struct orc_entry` with stack/base-pointer offsets, register selectors, type, and signal flag bitfields.

## Control Flow, State, and Persistence
No functions are present. `struct orc_entry` is persisted in generated unwind tables and interpreted by consumers to recover previous stack and base-pointer values at a code address.

## Dependencies and Integration
Includes `linux/types.h`, `linux/compiler.h`, and, for C builds, `asm/byteorder.h` to select bitfield layout. Integrated with objtool and unwinder code that reads or writes ORC records.

## Risks and Test Signals
Risks include endian bitfield drift, packed-layout ABI changes, and missing register categories for special entry-code frames. Test signals include ORC table generation, unwinder self-tests, packed size/layout checks, and cross-endian compile coverage.
