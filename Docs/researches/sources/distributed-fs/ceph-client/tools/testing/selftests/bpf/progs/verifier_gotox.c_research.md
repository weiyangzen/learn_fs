# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_gotox.c

## Purpose

`verifier_gotox.c` tests indirect jump-table support for `BPF_JA | BPF_X`. It verifies reserved-field rejection, jump table discovery, pointer type checking, map-backed instruction array reads, immutability of jump tables, subprogram boundaries, and duplicate table values.

## Important APIs, Types, and Functions

The file includes `filter.h` for low-level instruction definitions. It declares multiple socket programs that exercise indirect jumps and jump-table maps or readonly data. Expected diagnostics include reserved field use, no jump tables found, expected `PTR_TO_INSN`, invalid reads of `insn_array`, misaligned value access, invalid map-value bounds, negative index values, forbidden writes, and subprogram-boundary violations.

## Control Flow

Positive tests build a valid jump table, compute an index, and use an indirect jump to one of the table destinations. Negative tests deliberately set wrong destination register types, read misaligned or undersized jump entries, access table positions outside map bounds, attempt to modify readonly jump table data, branch outside the current subprogram, or encode non-unique target values.

## State and Persistence Behavior

Persistent state is jump-table data represented as map/global data. The verifier must treat table entries as immutable instruction references and preserve per-subprogram control-flow integrity.

## Dependencies and Integration Points

This file integrates with verifier instruction decoding, jump-table discovery, readonly map-value enforcement, subprogram control-flow validation, and JIT support for indirect BPF jumps.

## Risks and Test Signals

Risks are arbitrary control-flow through writable or malformed tables, crossing subprogram boundaries, and accepting reserved instruction fields. Test signals are successful valid jump-table loads and exact failures for bad register type, misalignment, invalid memory access, negative index, forbidden write, and outside-subprogram targets.
