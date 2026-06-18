# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/insn.h

## Purpose
Declares the public data structures and helper macros for x86 instruction decoding in tools. It describes how decoded prefixes, opcodes, ModRM/SIB, displacement, immediates, and mode-dependent sizes are represented.

## APIs, Types, and Functions
Core types are `struct insn_field`, `struct insn`, and `enum insn_mode`. It declares `insn_init()`, staged getters `insn_get_prefixes()` through `insn_get_length()`, `insn_decode()`, `insn_rip_relative()`, and inline helpers for REX2, VEX/EVEX/XOP fields, field offsets, and MOV/POP SS exception masking. Macros decode ModRM, SIB, REX, REX2, VEX, EVEX, and XOP bit fields.

## Control Flow, State, and Persistence
Decoder state is stored in `struct insn`: each field has a `got` bit, byte count, and value, while `next_byte` advances through the input buffer. Inline offset helpers derive byte offsets from field lengths after staged decoding. Endianness-specific `insn_field` logic keeps byte arrays in little-endian order even on big-endian hosts.

## Dependencies and Integration
Includes `asm/byteorder.h` and `inat.h`. Implemented by `lib/insn.c` and used by perf/objtool-style tooling that needs kernel-compatible instruction length and operand metadata without a full disassembler.

## Risks and Test Signals
Risks include incorrect endian handling, stale prefix bytes when repeated prefixes exceed the compact storage, and mismatched REX2/EVEX interpretation as the x86 ISA evolves. Test signals are decode tests for all field offsets, RIP-relative addressing, VEX2/VEX3/EVEX/XOP encodings, 32-bit versus 64-bit modes, and MOV/POP SS trap-suppression detection.
