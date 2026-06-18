# sources/distributed-fs/ceph-client/arch/x86/lib/insn.c

Purpose: implements the generic x86 instruction decoder that parses prefixes, opcodes, ModRM, SIB, displacement, immediates, and total instruction length into `struct insn`.

Important APIs/functions: defines `insn_init`, `insn_get_prefixes`, `insn_get_opcode`, `insn_get_modrm`, `insn_rip_relative`, `insn_get_sib`, `insn_get_displacement`, `insn_get_immediate`, `insn_get_length`, and `insn_decode`. Internal helpers parse Xen/KVM emulate prefixes and immediate variants.

Control flow: initialization caps buffers at `MAX_INSN_SIZE` and sets default operand/address sizes. Prefix parsing consumes optional Xen/KVM emulate prefixes, legacy prefixes, REX/REX2, VEX/XOP/EVEX prefixes, and updates address/operand sizes. Opcode parsing consults inat tables, handles VEX/XOP/REX2 maps, escapes, invalid64, groups, and must-VEX/EVEX constraints. Later stages lazily parse ModRM, SIB, displacement, and immediates according to attributes. `insn_decode()` runs the full length decode for a selected mode and rejects incomplete decodes.

State and persistence behavior: all state is in the caller-provided `struct insn`; no globals except read-only emulate-prefix arrays. It reads only the provided instruction buffer.

Dependencies/integration points: depends on generated inat attribute APIs, `asm/insn.h`, unaligned little-endian loads, emulate-prefix definitions, and Kconfig mode. Consumers include KVM, uprobes, alternatives, fault decoding, and MMIO emulation.

Risks: decoder must never read past the bounded buffer; `validate_next` guards all byte fetches. Prefix interactions are subtle, especially duplicate legacy prefixes, REX2 map bits, XOP ambiguity in 32-bit mode, EVEX scalable operands, and invalid instructions. Incorrect length decoding can corrupt patching/emulation.

Test signals: x86 instruction decoder test suites, fuzzing random byte streams under bounded buffers, AVX/EVEX/XOP/REX2 coverage, emulate-prefix tests, and KASAN checks for no over-read.
