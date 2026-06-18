# sources/distributed-fs/ceph-client/arch/csky/abiv1/alignment.c

## Purpose

handles C-SKY ABI v1 unaligned access traps by decoding selected load/store opcodes and emulating
them byte-by-byte when enabled

## Important APIs, Types, and Functions

Source read size: 340 lines, 5881 bytes. Includes: `linux/kernel.h`, `linux/uaccess.h`,
`linux/ptrace.h`. Functions: `get_ptreg`, `put_ptreg`, `ldb_asm`, `stb_asm`, `ldh_c`, `sth_c`,
`ldw_c`, `stw_c`, `csky_alignment`, `csky_alignment_init`. Key macros/defines: `OP_LDH`, `OP_STH`,
`OP_LDW`, `OP_STW`.

## Control Flow and Behavior

get_ptreg/put_ptreg access saved registers; ldb_asm/stb_asm use exception-table protected byte
accesses; ldh_c/sth_c/ldw_c/stw_c emulate halfword and word operations; csky_alignment() decodes the
faulting instruction, counts kernel/user events, and either fixes the access or delegates to
fixup_exception/signals

## State and Persistence

persistent state is the static enable flags and counters for kernel/user alignment handling

## Dependencies and Integration Points

integrates with trap handling, pt_regs layout, user access exception tables, and ABI v1 instruction
encoding

## Risks and Test Signals

incorrect opcode decoding or register mapping can corrupt user state or hide real faults; alignment-
trap tests, unaligned user loads/stores, and exception-fixup paths are key signals
