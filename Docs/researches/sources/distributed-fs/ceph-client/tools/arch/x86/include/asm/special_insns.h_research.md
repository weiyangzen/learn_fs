# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/special_insns.h

## Purpose
Wraps special x86 instructions needed by tools-side MMIO helpers.

## APIs, Types, and Functions
Exports `movdir64b(void *dst, const void *src)`, which emits the MOVDIR64B instruction bytes and constrains both source and destination as 64-byte memory objects.

## Control Flow, State, and Persistence
The helper casts the pointers to anonymous 64-byte structs, then issues volatile inline assembly using `rax` for destination and `rdx` for source. It performs one direct-store 64-byte transfer and does not add feature checks or barriers.

## Dependencies and Integration
Used by `io.h` through `iosubmit_cmds512()`. The caller must ensure CPU support, valid alignment, and MMIO destination semantics.

## Risks and Test Signals
Risks include illegal-instruction faults on CPUs without MOVDIR64B, unaligned destinations, and incorrect compiler reordering if constraints are changed. Test signals are feature-gated execution tests, generated assembly inspection, and MMIO submission tests on hardware that advertises the instruction.
