# sources/distributed-fs/ceph-client/arch/x86/include/asm/module.h

## Purpose
Defines x86 module architecture-specific metadata for ORC unwinding and indirect-target selection mitigation pages.

## Important APIs, Types, And Functions
Types include `struct its_array` with optional `pages` and `num`, and `struct mod_arch_specific` with ORC unwind table fields `num_orcs`, `orc_unwind_ip`, `orc_unwind`, plus `its_pages`.

## Control Flow
Module loader code fills this metadata when loading modules with ORC unwind data or ITS mitigation support. The header itself is structural.

## State And Persistence
State is per-loaded-module kernel memory. It persists until module unload.

## Dependencies And Integration Points
Depends on generic module metadata and `asm/orc_types.h`. It integrates with the ORC unwinder, module loader relocation, and mitigation code that allocates ITS thunk pages.

## Risks And Edge Cases
Incorrect ORC counts or pointers break stack unwinding through modules. ITS page lifetime must match module lifetime. Disabled config fields must not be referenced.

## Test Signals
Module load/unload tests, ORC unwinder stack traces through modules, livepatch/ftrace module coverage, and ITS mitigation build coverage are useful.
