# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/inst.h

Purpose: Provides an architecture-neutral wrapper type and helpers for PowerPC instructions, including support for prefixed 64-bit instructions on newer CPUs.

Important APIs, types, and functions: Defines `get_user_instr()`, `__get_user_instr()`, `ppc_inst_t` accessors, `ppc_inst()`, `ppc_inst_prefix()`, `ppc_inst_val()`, `ppc_inst_suffix()`, `ppc_inst_read()`, `ppc_inst_prefixed()`, `ppc_inst_swab()`, `ppc_inst_equal()`, `ppc_inst_len()`, `ppc_inst_next()`, `ppc_inst_as_ulong()`, `ppc_inst_write()`, and nofault copy helpers.

Control flow: Instruction decoders and patchers read a word, detect whether it is prefixed, fetch/write the suffix when needed, compare or byte-swap the logical instruction, and advance pointers by 4 or 8 bytes.

State and persistence: No state is stored. Helpers read/write kernel or user instruction memory.

Dependencies and integration points: Used by kprobes, ftrace, BPF, instruction emulation, patching, and fault-safe code reads. Depends on uaccess and nofault copy helpers.

Risks: Prefixed instruction length handling is critical for patching and stepping. User instruction fetch must be endian-correct and fault-safe. Treating prefixed instructions as single words can corrupt decoding.

Test signals: Decode normal and prefixed instructions, nofault copies across faults, pointer advancement, byte-swap equality, text patching of prefixed instructions, and 32-bit/non-prefixed build stubs.
