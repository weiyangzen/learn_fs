# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit_comp32.c

## Purpose
32-bit PA-RISC eBPF JIT backend. It lowers eBPF instructions onto a 32-bit big-endian HPPA ABI where 64-bit eBPF registers are represented as high/low 32-bit pairs, with some eBPF registers spilled into JIT scratch stack slots.

## Important APIs, Types, And Control Flow
The main exported entry points are `bpf_jit_emit_insn()`, `bpf_jit_build_prologue()`, and `bpf_jit_build_epilogue()`. The local `regmap` maps BPF registers to HPPA register pairs or negative stack offsets. Register helpers (`bpf_get_reg64()`, `bpf_put_reg64()`, `bpf_get_reg32()`, `bpf_put_reg32()`) load stacked values into temporary pairs and store them back. ALU helpers split 64-bit arithmetic into carry/borrow operations or call libgcc helpers (`__muldi3`, shifts) and PA-RISC millicode (`$$mulI`, `$$divU`, `$$remU`).

`bpf_jit_emit_insn()` dispatches eBPF opcodes: ALU/ALU64, endian swaps, direct branches, conditional 32/64-bit branches, helper calls, tail calls, loads/stores, and unsupported atomics. Branch helpers invert conditions for far branches and compensate for extra emitted instructions. The prologue sizes a PA-RISC stack frame, initializes the tail-call counter, saves only seen callee-saved registers where possible, copies incoming eBPF arguments from the HPPA ABI, and records an epilogue jump pointer. The epilogue restores saved registers and returns the low word of `BPF_REG_0`.

## State, Dependencies, Risks, And Tests
State lives in generated stack layout: saved HPPA registers, BPF scratch register pairs, BPF stack, tail-call counter, and an epilogue pointer. Dependencies include `bpf_jit.h`, Linux libgcc helpers, BPF verifier zero-extension metadata, PA-RISC millicode, and BPF array/program layouts for tail calls. Risks include high/low word ordering, big-endian load/store offsets, division-by-zero skip paths, far branch convergence, tail-call prologue skipping, and save elision based on `reg_seen`. Test with BPF ALU64 selftests, jmp32/jmp64 comparisons, helper-call argument preservation, tail-call exhaustion, unaligned/large-offset memory accesses, and unsupported atomic rejection.
