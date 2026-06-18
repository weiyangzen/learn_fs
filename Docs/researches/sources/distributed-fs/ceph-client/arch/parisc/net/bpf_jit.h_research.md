# sources/distributed-fs/ceph-client/arch/parisc/net/bpf_jit.h

## Purpose
Common PA-RISC eBPF JIT header shared by the 32-bit and 64-bit emitters. It defines the HPPA register numbers, JIT context/data structures, instruction encoding helpers, branch-offset helpers, cache/fill hooks, and the architecture-specific emitter/prologue/epilogue interfaces used by `bpf_jit_core.c`.

## Important APIs, Types, And Control Flow
`struct hppa_jit_context` carries the current `bpf_prog`, generated HPPA instruction buffer, instruction count, BPF-to-native offsets, prologue/body/epilogue lengths, and register-use collection flags. `struct hppa_jit_data` stores the allocated `bpf_binary_header`, executable image pointer, and context between multi-pass JIT phases. The header exposes `bpf_jit_build_prologue()`, `bpf_jit_build_epilogue()`, `bpf_jit_emit_insn()`, `hppa_div64()`, and `hppa_div64_rem()`.

Most macros encode PA-RISC instructions such as loads/stores, ALU ops, control-register moves, conditional branches, and long branches using `hppa_t*` format builders. `emit()` appends or counts one 4-byte HPPA instruction, allowing sizing passes and final emission to share code. `hppa_offset()` translates a BPF branch target into a native instruction delta using the collected offset table.

## State, Dependencies, Risks, And Tests
State is transient JIT state in `hppa_jit_context`; persistent output is the executable instruction image. Dependencies include Linux BPF/filter APIs, PA-RISC cache flushing, `REG_SZ`, and the arch emitters. The highest risks are incorrect bit reassembly for PA-RISC immediates, wrong branch displacement accounting around delay slots, and stale register-use collection causing prologue/epilogue save omissions. Test signals include BPF selftests with short/far jumps, JIT dumps compared against expected PA-RISC encodings, 32/64-bit builds, and icache-flush execution tests.
