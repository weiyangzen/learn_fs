# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes_asm.S

## Purpose
Assembly fixture file for the s390 kprobes KUnit suite. It emits target functions with known invalid probe offsets inside odd bytes or multi-halfword instructions.

## Important APIs, Types, And Functions
Macros `KPROBES_TARGET_START` and `KPROBES_TARGET_END` wrap each target with symbol/function annotations, an ftrace NOP, and an exported offset data symbol. Targets include `kprobes_target_in_insn4`, `kprobes_target_in_insn6_lo`, `kprobes_target_in_insn6_hi`, `kprobes_target_bp`, and `kprobes_target_odd`.

## Control Flow And State
Each target contains hand-encoded instruction halfwords/bytes and returns via `br %r14`. Labels mark intentionally invalid probe positions, and `SYM_DATA(name##_offs, .quad 1b - name)` records the offset from function start.

## Dependencies And Integration
Depends on s390 assembler/linkage macros and ftrace NOP generation. Used with `test_kprobes.c` under the kprobes sanity-test config.

## Risks And Test Signals
Risks include assembler encoding changes, ftrace prologue size assumptions, or offset labels accidentally becoming valid probe sites. Signals are KUnit pass/fail for probe offset validation and successful assembly/linking.
