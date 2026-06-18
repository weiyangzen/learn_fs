# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_common.h

Purpose: common classic BPF instruction encoding constants shared by socket filters and eBPF-adjacent userspace tooling. The header is a pure UAPI contract: it defines how to decode the low-level `code` byte of BPF instructions and the maximum instruction count accepted when `BPF_MAXINSNS` is not provided elsewhere.

Important APIs/types: there are no functions or structs. The API is the macro set `BPF_CLASS`, `BPF_SIZE`, `BPF_MODE`, `BPF_OP`, and `BPF_SRC`, plus opcode/class constants such as `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_ALU`, `BPF_JMP`, `BPF_RET`, sizes `BPF_W/H/B`, modes `BPF_IMM/ABS/IND/MEM/LEN/MSH`, ALU ops, jump ops, and sources `BPF_K` and `BPF_X`.

Control flow, state, and persistence: all behavior is compile-time bit masking. Runtime control flow lives in kernel BPF interpreters/JITs and consumers such as `filter.h`, which use these masks to classify instructions. The only state-like value is `BPF_MAXINSNS`, an ABI limit macro rather than persistent state.

Dependencies and integration points: used by Linux socket-filter definitions and by userspace assemblers/disassemblers that build `struct sock_filter` arrays. Integration risk is semantic drift: changing bit values or masks would break compiled filters and tools that share BSD-compatible BPF encodings.

Risks and test signals: verify by compiling userspace filter programs, decoding known filter bytecode, and running socket filter attach tests. Tests should include instruction class/mode/op round-trips and boundary handling around `BPF_MAXINSNS`.
