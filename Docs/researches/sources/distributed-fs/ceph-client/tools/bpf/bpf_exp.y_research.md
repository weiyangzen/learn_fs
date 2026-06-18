<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y

Purpose: this bison grammar parses classic BPF assembly and emits `struct sock_filter` instructions. It also resolves symbolic labels into classic BPF branch offsets.

Important APIs/types/functions: grammar rules map load/store, jump, ALU, return, and misc instructions to `BPF_*` opcodes through `bpf_set_curr_instr()`. `bpf_set_curr_label()` and `bpf_set_jmp_label()` collect labels for current instruction and pending branch targets. `bpf_stage_1_insert_insns()` runs `yyparse()`, `bpf_stage_2_reduce_labels()` resolves `k`, `jt`, and `jf` labels, and `bpf_asm_compile()` orchestrates init, parse, reduction, cleanup, and output. Static arrays include `out[BPF_MAXINSNS]` and label arrays for direct jumps and true/false branch labels.

Control flow: parse productions accept classic forms for absolute/indirect loads, packet length, memory slots, immediate loads, `ldxb 4*([off]&0xf)`, stores, unconditional jumps, conditional jumps with one or two labels, inverse convenience jumps (`jneq`, `jlt`, `jle` encoded by swapping false branches), ALU ops with constants or X, returns, and A/X transfers. After parsing, unconditional `JA` labels are resolved to signed deltas stored in `k`; conditional labels are resolved to 8-bit forward offsets in `jt` and `jf`.

State and persistence: compiler state is process-local static state reset in `bpf_init()` and freed in `bpf_destroy()`. Output is printed to stdout. There is no persistent storage. Fatal parse, allocation assertion, label, and range errors call `exit(1)`.

Dependencies and integration points: it depends on `linux/filter.h`, generated lexer tokens, and classic BPF instruction encoding. `bpf_asm.c` provides the CLI, and `bpf_dbg.c` can consume the non-C output format.

Risks: conditional jump labels can only target forward instructions because `bpf_encode_jt_jf_offset()` rejects negative offsets and offsets above 255, matching classic BPF branch encoding but surprising users. Unconditional `JA` negative offsets are stored through unsigned `k`; kernel validation may reject unsafe loops, but assembler messaging is limited. `assert()` is used for label-array allocation. Label memory is freed only after successful parse/reduction; fatal exits leak process memory. Duplicate labels resolve to the first matching label with no diagnostic.

Test signals: parser tests should cover every production, label resolution, out-of-range conditional jumps, missing labels, duplicate labels, maximum instruction count, C-style and numeric output, inverse branch aliases, and kernel validation of assembled programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.y -->
