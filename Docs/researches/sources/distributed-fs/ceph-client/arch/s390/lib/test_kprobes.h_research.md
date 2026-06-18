# sources/distributed-fs/ceph-client/arch/s390/lib/test_kprobes.h

## Purpose
Header shared by the s390 kprobes KUnit C test and assembly target file.

## Important APIs, Types, And Functions
Declares four external offset symbols: `kprobes_target_odd_offs`, `kprobes_target_in_insn4_offs`, `kprobes_target_in_insn6_lo_offs`, and `kprobes_target_in_insn6_hi_offs`.

## Control Flow And State
No executable control flow. The declared symbols are data emitted by assembly macros and consumed as invalid offsets by the C KUnit tests.

## Dependencies And Integration
Depends on the companion assembly file for definitions and the C test for use. It is part of the `test_kprobes_s390` composite object.

## Risks And Test Signals
Risks are declaration/definition mismatch or symbol type/width mismatch. Signals are successful linkage of the KUnit test object and runtime kprobes KUnit execution.
