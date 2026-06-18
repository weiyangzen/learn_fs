# sources/distributed-fs/ceph-client/arch/s390/lib/probes.c

## Purpose
Shared s390 helper logic for kprobes and uprobes instruction validation/fixup.

## Important APIs, Types, And Functions
`probe_is_prohibited_opcode()` rejects unsupported or unsafe instructions such as DIAG, EXECUTE/EXRL, transactional-execution instructions, PSW/program-call instructions, and unknown opcodes. `probe_get_fixup_type()` classifies branch/link/PSW instructions into fixup strategies such as normal PSW advance, return-register fixup, branch-not-taken, or not-required. `probe_is_insn_relative_long()` detects RIL-b/RIL-c long relative instructions that need modification to avoid full emulation.

## Control Flow And State
All logic is stateless table-like opcode decoding over a `u16 *insn` instruction stream. It first validates the instruction with the s390 disassembler, then uses primary opcode and selected extension fields to select behavior.

## Dependencies And Integration
Depends on `asm/kprobes.h`, s390 instruction decoder/disassembler helpers, kprobe fixup constants, and CONFIG_KPROBES/UPROBES build selection.

## Risks And Test Signals
Risks include allowing unsafe opcodes, rejecting valid probe sites, incorrect branch fixup causing wrong resumed PSW, and missing new relative-long opcodes. Signals include kprobe/uprobe selftests, the s390 KUnit kprobes sanity suite, probe registration over branch opcodes, and instruction decoder updates.
