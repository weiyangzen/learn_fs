# sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.c

## Purpose
`pf_in.c` is the x86 instruction decoder used by mmiotrace page-fault interception. It classifies simple MMIO load/store instructions and extracts register, immediate, and memory access widths from the faulting instruction stream so mmiotrace can report what a trapped access attempted.

## Important APIs, Types, and Functions
The exported local interface from `pf_in.h` is implemented by `get_ins_type()`, `get_ins_mem_width()`, `get_ins_reg_val()`, and `get_ins_imm_val()`. Internal helpers include `skip_prefix()`, `get_opcode()`, `get_ins_reg_width()`, `get_reg_w8()`, and `get_reg_w32()`. Opcode tables classify register reads, register writes, immediate writes, and 8/16/32/64-bit memory widths, with separate i386 and amd64 prefix/opcode handling.

## Control Flow and State
Each decoder starts at `ins_addr`, strips recognized prefixes, including operand-size and REX prefixes on amd64, reads one- or two-byte opcodes, and searches static opcode arrays. Register-value extraction decodes the ModR/M register field, accounts for REX.R extension, treats `STOS` as fixed to AX, and returns a value from `struct pt_regs` using the inferred operand width. Immediate extraction skips ModR/M displacement forms before reading the immediate payload.

## State and Persistence
The file has no persistent mutable state beyond static opcode tables. It reads the faulting instruction bytes and saved register frame and emits diagnostic `printk()` errors for unsupported or malformed instructions.

## Dependencies and Integration Points
It depends on x86 instruction encoding, `struct pt_regs`, kernel `ARRAY_SIZE`, and the mmiotrace page-fault path that includes `pf_in.h`. It is intentionally narrow rather than a full instruction decoder.

## Risks and Test Signals
Risks include incomplete opcode coverage, unsafe instruction-byte reads if the faulting IP is unexpected, partial SIB/address-size handling in immediate decoding, and register-width mistakes around REX byte-register semantics. Test signals are mmiotrace logs showing correct read/write/immediate classification and widths for `ioread*()`, `iowrite*()`, and string-store patterns, plus error logs only for intentionally unsupported instructions.
