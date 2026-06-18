# sources/distributed-fs/ceph-client/arch/mips/include/asm/uasm.h

## Purpose

`uasm.h` declares the MIPS micro-assembler used to build runtime-generated instruction streams, especially TLB refill/fault handlers.

## Important APIs, Types, And Functions

The API is the large set of `uasm_i*` instruction emitters, label/relocation structs, `UASM_i_*` ABI-width aliases, safe 64-bit shift/rotate helpers, label builders, relocation movers, and labeled branch helpers. Includes: `linux/types.h`, `linux/export.h`. Macros/constants: `__ASM_UASM_H`, `UASM_EXPORT_SYMBOL`, `Ip_u1u2u3`, `Ip_u2u1u3`, `Ip_u3u2u1`, `Ip_u3u1u2`, `Ip_u1u2s3`, `Ip_u2s3u1`, `Ip_s3s1s2`, `Ip_u2u1s3`, `Ip_u2u1msbu3`, `Ip_u1u2`, `Ip_u2u1`, `Ip_u1s2`, `Ip_u1`, `Ip_0`, `UASM_L_LA`, `UASM_i_ADDIU`, `UASM_i_ADDU`, `UASM_i_LL`, `UASM_i_LW`, `UASM_i_LWX`, `UASM_i_MFC0`, `UASM_i_MTC0`, `UASM_i_ROTR`, `UASM_i_SC`, `UASM_i_SLL`, `UASM_i_SRA`, `UASM_i_SRL`, `UASM_i_SRL_SAFE`, `UASM_i_SUBU`, `UASM_i_SW`, `uasm_i_b`, `uasm_i_beqz`, and 8 more. Types/enums/unions: `uasm_label`, `uasm_reloc`. Functions/prototypes/helpers: `uasm_build_label`, `uasm_in_compat_space_p`, `uasm_rel_hi`, `uasm_rel_lo`, `UASM_i_LA_mostly`, `UASM_i_LA`, `uasm_i_drotr_safe`, `uasm_i_dsll_safe`, `uasm_i_dsrl_safe`, `uasm_i_dsra_safe`, `uasm_r_mips_pc16`, `uasm_resolve_relocs`, `uasm_move_relocs`, `uasm_move_labels`, `uasm_copy_handler`, `uasm_insn_has_bdelay`, `uasm_il_b`, `uasm_il_bbit0`, `uasm_il_bbit1`, `uasm_il_beq`, `uasm_il_beqz`, `uasm_il_beqzl`, `uasm_il_bgezl`, `uasm_il_bgez`, `uasm_il_bltz`, `uasm_il_bne`, `uasm_il_bnez`, `Ip_u2u1s3`, `Ip_u3u1u2`, `Ip_u2u1u3`, and 19 more.

## Control Flow

Callers append encoded instructions to a `u32 **buf`, place labels, record relocations, then resolve or copy handlers into final executable memory.

## State And Persistence

State is caller-owned instruction buffers plus label/relocation arrays; no global persistence except optional exported symbols when `CONFIG_EXPORT_UASM` is enabled.

## Dependencies And Integration Points

It integrates with TLB exception generation, CPU feature-dependent code emission, module exports, and instruction encoding definitions.

## Risks

Risks are bad instruction encoding, unresolved relocations, branch-delay-slot mistakes, 32/64-bit alias mismatch, or generating code unsupported by the target ISA.

## Test Signals

Test signals are boot TLB refill paths, objdump of generated handlers, QEMU/hardware boots across CPU revisions, and runtime TLB miss stress.
Static review signal: this source currently has 329 lines and 9664 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
