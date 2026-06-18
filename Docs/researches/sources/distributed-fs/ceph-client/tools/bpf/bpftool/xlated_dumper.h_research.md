# sources/distributed-fs/ceph-client/tools/bpf/bpftool/xlated_dumper.h

Purpose: Declares data structures and dump function prototypes used by bpftool translated-instruction dumpers.

Important APIs, types, and functions: `struct kernel_sym` stores address, name, and module. `struct dump_data` carries kallsyms, JIT ksym array, BTF, function info, line info, and scratch buffer. Function declarations cover symbol loading/search/destruction and JSON/plain/graph xlated dumping.

Control flow: Not applicable in the header, but callers initialize `dump_data`, optionally load symbols, and pass instruction buffers to one of the dump functions.

State and persistence: No static state. The caller owns `dump_data` lifecycle and must call `kernel_syms_destroy()` after `kernel_syms_load()`.

Dependencies and integration points: Included by `prog.c`, `xlated_dumper.c`, and CFG dumping code. References `struct bpf_prog_linfo`, `struct btf`, and bpftool/libbpf types through included compilation units.

Risks: Header layout is a cross-file ABI inside bpftool; changes to `dump_data` require all dump users to initialize new fields. Scratch buffer size constrains symbol/immediate rendering.

Test signals: Compile bpftool and run all xlated dump modes; missing initialization usually appears as bad symbol names or null BTF/line output.
