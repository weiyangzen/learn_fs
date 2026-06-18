# sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.c

Purpose: Formats translated BPF instructions for bpftool dump output in plain text, JSON, and DOT graph labels, with helper/subprogram/map immediate annotation and optional BTF line/function info.

Important APIs, types, and functions: `kernel_syms_load()`, `kernel_syms_destroy()`, and `kernel_syms_search()` manage `/proc/kallsyms` lookup. `print_call()` resolves helper and pseudo-call targets. `print_imm()` annotates map fd/value/index and pseudo-function immediates. `dump_xlated_json()`, `dump_xlated_plain()`, and `dump_xlated_for_graph()` iterate `struct bpf_insn` arrays and call `print_bpf_insn()` with callbacks.

Control flow: Kallsyms load reads symbols, records `__bpf_call_base`, rejects restricted zero addresses, and sorts by address. Dump functions skip the second half of double-wide `BPF_LD | BPF_IMM | BPF_DW` instructions, emit function prototypes when `func_info` offsets match, emit line info via `bpf_prog_linfo__lfind()`, print disassembly, and optionally print raw opcodes.

State and persistence: State is contained in `struct dump_data`; `scratch_buff` is reused by callbacks. No persistence.

Dependencies and integration points: Called from `prog.c` dump and loader debug paths and from CFG visual code. Depends on libbpf disassembler callbacks, BTF dumper helpers, bpftool JSON writer, and `/proc/kallsyms` visibility.

Risks: `kernel_syms_cmp()` subtracts unsigned long addresses into int, which follows existing code but can be sensitive to large deltas. Graph escaping uses fixed 64-byte buffer and truncates long instruction strings. Kallsyms restrictions reduce helper and subprogram annotation quality.

Test signals: Dump xlated instructions with helpers, map immediates, pseudo-calls, double-wide loads, BTF function/line info, JSON opcodes, and DOT graph output.
