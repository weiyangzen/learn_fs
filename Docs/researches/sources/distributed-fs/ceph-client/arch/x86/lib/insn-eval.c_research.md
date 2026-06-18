# sources/distributed-fs/ceph-client/arch/x86/lib/insn-eval.c

Purpose: evaluates decoded x86 instructions against a `pt_regs` frame to resolve registers, segment bases/limits, effective addresses, instruction fetch addresses, MMIO access types, and recognized NOPs.

Important APIs/functions: exports/defines `insn_has_rep_prefix`, `pt_regs_offset`, `insn_get_seg_base`, `insn_get_code_seg_params`, `insn_get_modrm_rm_off`, `insn_get_modrm_reg_off`, `insn_get_modrm_reg_ptr`, `insn_get_addr_ref`, `insn_get_effective_ip`, `insn_fetch_from_user`, `insn_fetch_from_user_inatomic`, `insn_decode_from_regs`, `insn_decode_mmio`, and `insn_is_nop`. Internal helpers resolve segment overrides, selectors, descriptor tables, ModRM/SIB register offsets, 16/32/64-bit effective addresses, and segment limits.

Control flow: segment resolution first considers long mode, string-instruction constraints, override prefixes, and default segment rules. Descriptor lookup reads LDT or GDT where valid. Address resolution decodes ModRM/SIB/displacements, gets register values from `pt_regs`, applies segment base and limit checks for 16/32-bit modes, and returns a user linear address or `-1L`. Fetch helpers compute effective IP and copy instruction bytes from user memory. MMIO decode maps MOV/MOVS/MOVSX/MOVZX opcodes to read/write types and byte widths. NOP recognition checks opcode/prefix/ModRM/SIB patterns without allowing false positives like PAUSE.

State and persistence behavior: mostly read-only over instruction buffers, descriptors, MSRs, current mm LDT, and user memory. It writes output buffers and may take `current->mm->context.lock` for LDT lookup. No persistent state.

Dependencies/integration points: uses the instruction decoder (`insn.c`/inat), x86 descriptor/LDT/MSR/vm86 helpers, uaccess, pt_regs accessors, and MMIO/emulation consumers. Fault handlers, uprobes, alternatives, and emulators rely on these utilities.

Risks: x86 addressing rules are complex across real/v8086/protected/long modes, 16-bit address encodings, FS/GS bases, REX/REX2 extensions, and segment limits. Misresolving addresses can produce wrong fault emulation or security bugs. LDT access requires valid context and locking. NOP detection must avoid false positives because callers may skip or compress instructions.

Test signals: instruction/address decoder tests across 16/32/64-bit modes, LDT/vm86 cases, FS/GS base tests, MMIO decode tests for supported MOV forms, user fetch fault tests, and NOP recognition tests including PAUSE and VEX exclusions.
