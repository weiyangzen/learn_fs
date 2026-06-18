
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h

## Purpose
Defines the common classic BPF instruction encoding constants shared by user space and kernel code. The header is the low-level bit layout for decoding a BPF opcode into instruction class, load size, addressing mode, ALU/jump operation, source operand, and maximum classic-program length.

## APIs, Control Flow, and State
The API is macro-only: `BPF_CLASS()`, `BPF_SIZE()`, `BPF_MODE()`, `BPF_OP()`, and `BPF_SRC()` mask opcode fields, while constants such as `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_ALU`, `BPF_JMP`, `BPF_RET`, `BPF_W/H/B`, `BPF_IMM/ABS/IND/MEM/LEN/MSH`, ALU ops, jump ops, `BPF_K`, and `BPF_X` name field values. `BPF_MAXINSNS` defaults to 4096 if an includer has not provided a different value. There is no executable control flow or persistent state in the header; state lives in BPF program arrays and verifier/runtime users that interpret these bit fields.

## Dependencies, Integration, Risks, and Tests
The header is dependency-light and integrates with socket filters, seccomp, BPF loaders, disassemblers, and kernel compatibility code that still parses classic BPF opcodes. Risks are ABI drift in numeric opcode values, callers confusing classic BPF encodings with eBPF-only extensions, and out-of-tree code overriding `BPF_MAXINSNS` inconsistently. Test signals include classic socket-filter load tests, seccomp filter tests, BPF assembler/disassembler round trips, and compile checks for tools that include only UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h -->
