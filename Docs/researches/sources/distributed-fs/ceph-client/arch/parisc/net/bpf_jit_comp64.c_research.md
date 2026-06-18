# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp64.c

## Purpose
64-bit PA-RISC eBPF JIT backend. It maps eBPF registers to native 64-bit HPPA registers, emits PA-RISC 2.0 wide-mode instructions, handles PA-RISC function descriptors, and advertises kfunc-call support.

## Important APIs, Types, And Control Flow
`bpf_jit_emit_insn()` is the opcode dispatcher. It uses `init_regs()` to map BPF operands, emits native ALU operations where possible, and calls libgcc/division helpers for multiply, division, modulo, and 64-bit helper arithmetic paths. Immediate emission uses `emit_imm32()` and `emit_imm()` to synthesize 64-bit constants. Shift/extract/deposit helpers (`emit_hppa64_depd`, `emit_hppa64_extrd`, `emit_hppa64_shld`, `emit_hppa64_shrd`) implement zero/sign extension, shifts, and endian conversion.

Control flow is built by `emit_branch()` and `emit_jump()`. Near conditional branches reserve two no-ops to stabilize sizing; far branches invert the condition and jump over a long branch. Helper calls marshal BPF arguments to PA-RISC ABI argument registers and load code address/gp from `elf64_fdesc`. Tail calls validate index, decrement the tail-call counter, load `prog->bpf_func`, and jump past the target prologue initializer.

## State, Dependencies, Risks, And Tests
Persistent output is the executable JIT image plus its inline function descriptor words in the prologue. Runtime state includes the upward-growing HPPA stack frame, saved callee registers, BPF stack, tail-call counter, gp, and epilogue pointer. Dependencies include `struct elf64_fdesc`, BPF aux verifier-zext metadata, libgcc helpers, BPF array layout, and PA-RISC 64 kernel address constraints below 4GB for some branch materialization. Risks include function descriptor/gp corruption, 32-bit ALU zero-extension, branch-size convergence, unaligned doubleword load/store handling, probe-memory load behavior, and the extra epilogue nop noted in-source. Test with BPF selftests under 64-bit PA-RISC, kfunc/helper calls, pseudo-function immediates, tail calls, endian swaps, jmp32 signed/unsigned cases, and large JIT images.
