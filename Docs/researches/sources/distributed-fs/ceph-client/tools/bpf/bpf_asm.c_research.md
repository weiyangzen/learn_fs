<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c

Purpose: this is the minimal command-line driver for the classic BPF assembler. It reads an assembler program from stdin or the first openable filename argument and calls the parser/compiler to emit classic BPF bytecode in comma format or C initializer format.

Important APIs/functions: `main()` handles `-c`, opens an input file if supplied, and calls external `bpf_asm_compile(FILE *fp, bool cstyle)` implemented by the bison grammar in `bpf_exp.y`. `cstyle` controls whether output is `{ code, jt, jf, k }` initializer lines or `len,code jt jf k,...` format suitable for other tools.

Control flow: arguments are scanned left to right. Any argument beginning with `-c` enables C-style output. The first subsequent argument that can be opened becomes input; failed opens are ignored and stdin remains selected. There is no explicit usage output or error exit for nonexistent files.

State and persistence: no persistent state is written. The input file stream is closed by `bpf_asm_compile()` if it is not stdin. Output goes to stdout.

Dependencies and integration points: it depends on the generated lexer/parser and classic BPF definitions in `linux/filter.h`. Its output can be consumed by `bpf_dbg`, socket filter loaders, tc/xt_bpf-related tooling, or test fixtures.

Risks: silently falling back to stdin on open failure can confuse scripts. `-cfoo` is accepted as `-c` because `strncmp("-c", argv[i], 2)` is used. There is no validation in this wrapper; parse and instruction-limit errors abort inside the compiler.

Test signals: assemble from stdin and file, check `-c` output, check nonexistent file behavior, and compare parser output against known `tcpdump -ddd` or documented classic BPF examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_asm.c -->
