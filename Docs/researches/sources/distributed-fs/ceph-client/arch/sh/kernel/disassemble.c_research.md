# sources/distributed-fs/ceph-client/arch/sh/kernel/disassemble.c

Purpose: prints symbolic SuperH instruction disassembly around a faulting PC for diagnostics.

Important APIs and control flow: the `sh_table[]` opcode table encodes instruction names, argument types, and nibble patterns. `print_sh_insn()` matches a 16-bit instruction, extracts registers/displacements/immediates, formats operands, and resolves PC-relative loads to symbol-like comments when possible. `show_code()` validates even PC alignment, reads three instructions before through five after the current PC with `__get_user()`, marks the current instruction, and prints decoded output.

State, dependencies, and risks: state is static opcode metadata. Dependencies include `pt_regs`, user/kernel fault-safe reads, `%pS` symbolization, and SH instruction encoding knowledge. Risks are stale/incomplete opcode coverage, faulting while dereferencing PC-relative targets, and misleading output for newer extensions. Test signals are oops logs with code dumps, explicit invalid address handling, and table comparisons against known SH encodings.
