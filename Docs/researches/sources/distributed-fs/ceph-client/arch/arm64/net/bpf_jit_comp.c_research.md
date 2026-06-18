# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit_comp.c

## Purpose

implements the arm64 eBPF JIT backend, including instruction selection, BPF program
prologue/epilogue generation, tail calls, exception-table fixups, trampoline generation, text
patching, and capability reporting to the generic BPF core

## Important APIs, Types, and Functions

Source read size: 3161 lines, 87356 bytes. Includes: `linux/arm-smccc.h`, `linux/bitfield.h`,
`linux/bpf.h`, `linux/cfi.h`, `linux/filter.h`, `linux/memory.h`, `linux/printk.h`, `linux/slab.h`,
`asm/asm-extable.h`, `asm/byteorder.h`; plus 6 more. Functions: `emit`, `emit_u32_data`,
`emit_a64_mov_i`, `i64_i16_blocks`, `emit_a64_mov_i64`, `emit_bti`, `emit_kcfi`,
`emit_addr_mov_i64`, `should_emit_indirect_call`, `emit_direct_call`, `emit_indirect_call`,
`emit_call`, `bpf2a64_offset`, `jit_fill_hole`, `bpf_arch_text_invalidate`, `epilogue_offset`,
`is_addsub_imm`, `emit_a64_add_i`; plus 54 more. Key macros/defines: `pr_fmt(fmt)`, `TMP_REG_1`,
`TMP_REG_2`, `TCCNT_PTR`, `TMP_REG_3`, `PRIVATE_SP`, `ARENA_VM_START`, `check_imm(bits, imm)`,
`check_imm19(imm)`, `check_imm26(imm)`, `PLT_TARGET_SIZE`, `PLT_TARGET_OFFSET`,
`PRIV_STACK_GUARD_SZ`, `PRIV_STACK_GUARD_VAL`, `BTI_INSNS`, `PAC_INSNS`, `POKE_OFFSET`,
`PROLOGUE_OFFSET`; plus 5 more. Local structs: `jit_ctx`, `bpf_plt`, `bpf_prog_aux`, `pt_regs`,
`exception_table_entry`, `bpf_prog`, `arm64_jit_data`, `bpf_binary_header`; plus 3 more.

## Control Flow and Behavior

the compiler performs size estimation, offset discovery, final emission, validation, executable pack
finalization, and optional multi-function extra passes; instruction emission maps BPF registers onto
AArch64 registers and lowers ALU, jump, load/store, atomic, helper-call, arena, percpu, and timed-
may-goto operations

## State and Persistence

persistent effects are the generated read-only executable image, BPF line-info offsets,
aux->jit_data during subprogram linking, exception-table entries, optional per-CPU private stack
allocation guarded by sentinel values, and trampoline patch sites/PLT targets

## Dependencies and Integration Points

depends on the BPF verifier/core, arm64 instruction encoding and text patching APIs, BTI/PAC/KCFI
controls, cpufeature detection, executable BPF program packs, exception tables, ftrace-style
trampoline attachment, and arm64 speculation mitigations

## Risks and Test Signals

branch offset ranges, stack layout, register save/restore order, exception metadata encoding,
private-stack guard accounting, long-jump PLT patching, and LSE versus LL/SC atomic selection are
correctness-critical; test signals are BPF selftests, JIT dump validation, verifier JIT coverage,
trampoline/fentry/fexit tests, kprobe/fprobe exercises, and boot/runtime warnings from validate_ctx
or text poke failures
