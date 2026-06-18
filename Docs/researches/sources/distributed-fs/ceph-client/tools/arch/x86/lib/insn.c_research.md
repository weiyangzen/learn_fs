# sources/distributed-fs/ceph-client/tools/arch/x86/lib/insn.c

## Purpose
Implements staged x86 instruction decoding for tools, including prefix parsing, opcode attribute lookup, ModRM/SIB/displacement/immediate decoding, instruction length computation, and mode-specific validation.

## APIs, Types, and Functions
Exports `insn_init()`, `insn_get_prefixes()`, `insn_get_opcode()`, `insn_get_modrm()`, `insn_rip_relative()`, `insn_get_sib()`, `insn_get_displacement()`, `insn_get_immediate()`, `insn_get_length()`, and `insn_decode()`. Internal helpers include buffer-safe `get_next`/`peek_next` macros, emulate-prefix scanning, `__get_moffset()`, `__get_immv32()`, `__get_immv()`, `__get_immptr()`, and `insn_complete()`.

## Control Flow, State, and Persistence
Decoding starts with `insn_init()`, clamps buffers to 15 bytes, sets default operand/address sizes, and advances `next_byte` as fields are consumed. Prefix decoding handles Xen/KVM emulate prefixes, legacy prefix deduplication, address/operand-size toggles, REX/REX2, and VEX/EVEX/XOP. Opcode decoding follows escape/group/AVX/XOP tables and rejects illegal VEX/EVEX or invalid 64-bit forms. Later stages decode ModRM groups, SIB, addressing-mode displacements, moffsets, immediates, and final length.

## Dependencies and Integration
Depends on Linux helper headers for string, unaligned access, errno, kconfig, `inat.h`, `insn.h`, and `emulate_prefix.h`. Integrated with perf/objtool-style consumers needing instruction length and addressing information.

## Risks and Test Signals
Risks include off-by-one buffer validation, prefix overflow behavior, incomplete REX2/EVEX ISA coverage, subtle operand-size rules, and invalid instruction handling that may still leave partial state. Test signals are fuzzing over byte streams, golden decode tests for legacy/REX/VEX/EVEX/XOP, RIP-relative checks, immediate-size matrix tests, and truncated-buffer `-ENODATA` paths.
