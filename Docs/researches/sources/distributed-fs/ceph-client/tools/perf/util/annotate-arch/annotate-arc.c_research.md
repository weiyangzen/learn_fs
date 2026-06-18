# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arc.c

## Purpose

`annotate-arc.c` creates the ARC architecture descriptor used by perf annotation/disassembly.

## Important APIs, Types, and Functions

It implements `arch__new_arc`, allocating `struct arch`, setting `name = "arc"`, copying machine ID flags, and configuring objdump comment character `;`.

## Control Flow and State

The function allocates with `zalloc`, returns `NULL` on failure, and otherwise returns the initialized architecture object as `const struct arch *`.

## Dependencies and Integration Points

It depends on the generic disasm architecture model and is selected when perf annotates ARC binaries.

## Risks and Test Signals

Risks are minimal but include missing ARC-specific instruction classification. Tests should disassemble ARC code and verify comments are parsed correctly.
