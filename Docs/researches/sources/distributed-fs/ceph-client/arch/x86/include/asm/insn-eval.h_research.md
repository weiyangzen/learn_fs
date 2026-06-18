<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h

## Purpose
Instruction evaluation helpers for fault/emulation paths that need effective addresses, segment bases, register pointers, and instruction-relative calculations. The header is 49 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/compiler.h>`; `#include <linux/bug.h>`; `#include <linux/err.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_INSN_EVAL_H`; `#define INSN_CODE_SEG_ADDR_SZ(params) ((params >> 4) & 0xf)`; `#define INSN_CODE_SEG_OPND_SZ(params) (params & 0xf)`; `#define INSN_CODE_SEG_PARAMS(oper_sz, addr_sz) (oper_sz | (addr_sz << 4))`

Notable declarations and inline helpers: `#define _ASM_X86_INSN_EVAL_H`; `#define INSN_CODE_SEG_ADDR_SZ(params) ((params >> 4) & 0xf)`; `#define INSN_CODE_SEG_OPND_SZ(params) (params & 0xf)`; `#define INSN_CODE_SEG_PARAMS(oper_sz, addr_sz) (oper_sz | (addr_sz << 4))`; `int pt_regs_offset(struct pt_regs *regs, int regno);`; `bool insn_has_rep_prefix(struct insn *insn);`; `void __user *insn_get_addr_ref(struct insn *insn, struct pt_regs *regs);`; `int insn_get_modrm_rm_off(struct insn *insn, struct pt_regs *regs);`; `int insn_get_modrm_reg_off(struct insn *insn, struct pt_regs *regs);`; `unsigned long *insn_get_modrm_reg_ptr(struct insn *insn, struct pt_regs *regs);`; `unsigned long insn_get_seg_base(struct pt_regs *regs, int seg_reg_idx);`; `int insn_get_code_seg_params(struct pt_regs *regs);`; `int insn_get_effective_ip(struct pt_regs *regs, unsigned long *ip);`; `int insn_fetch_from_user(struct pt_regs *regs,`; `unsigned char buf[MAX_INSN_SIZE]);`; `int insn_fetch_from_user_inatomic(struct pt_regs *regs,`; `bool insn_decode_from_regs(struct insn *insn, struct pt_regs *regs,`; `unsigned char buf[MAX_INSN_SIZE], int buf_size);`; `enum insn_mmio_type {`; `enum insn_mmio_type insn_decode_mmio(struct insn *insn, int *bytes);`; `bool insn_is_nop(struct insn *insn);`

## Control Flow
Exception handlers decode an instruction, resolve ModRM/SIB/displacement and segment context, then compute memory references or register operands for fixups/emulation.

## State and Persistence
State is transient pt_regs plus decoded insn data; no persistent storage is defined here.

## Dependencies and Integration Points
Depends on insn.h, ptrace registers, segment/FSGS state, uaccess-safe memory probing, and exception/fixup users such as UMIP or SEV-ES.

## Risks
Risks include wrong address-size/sign-extension rules, segment-base mistakes, and unsafe register pointer mapping in fault contexts.

## Test Signals
Tests should cover effective-address decoding for ModRM/SIB/RIP-relative forms, 32/64-bit modes, segment overrides, user/kernel regs, and malformed instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h -->
