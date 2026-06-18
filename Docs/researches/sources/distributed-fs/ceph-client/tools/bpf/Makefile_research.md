<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/Makefile

Purpose: this Makefile builds and installs the standalone BPF tools `bpf_jit_disasm`, `bpf_dbg`, and `bpf_asm`, and delegates to `bpftool` and `resolve_btfids`. It also generates lexer/parser sources for the classic BPF assembler.

Important targets/variables: `PROGS` lists the three standalone binaries. Pattern rules generate `%.yacc.c` with bison and `%.lex.c` with flex, compile objects, and link binaries. `FEATURE_TESTS` checks `libbfd` and disassembler ABI variants; `feature-disassembler-four-args` and `feature-disassembler-init-styled` add compatibility defines. Targets include `all`, `clean`, `install`, `bpftool`, `bpftool_install`, `bpftool_clean`, `resolve_btfids`, and `resolve_btfids_clean`.

Control flow: the Makefile derives `srctree` for in-tree and selftests/out-of-tree invocation, conditionally includes feature detection unless the goal is only clean-like, compiles objects under `$(OUTPUT)`, links `bpf_jit_disasm` with libopcodes/libbfd/libdl, `bpf_dbg` with readline, and `bpf_asm` with generated parser/lexer objects. `all` always includes delegated `bpftool`.

State and persistence: build products live under `$(OUTPUT)` when set or the source directory otherwise. Generated state includes `.o`, generated yacc/lex files, feature dumps, and delegated build outputs. Install persists binaries under `$(DESTDIR)$(prefix)/bin`.

Dependencies and integration points: it depends on kernel tools make infrastructure, flex, bison, libbfd/opcodes, readline, and exported kernel headers. It is integrated into the larger kernel tools build and selftests environments.

Risks: feature detection is skipped for some clean targets only; missing libbfd/readline/flex/bison will fail relevant builds. If `OUTPUT` is unset, generated files can appear in the source directory. `bpf_jit_disasm` ABI compatibility depends on feature probes matching the installed binutils headers and libraries.

Test signals: useful checks are `make -C tools/bpf`, `make clean`, out-of-tree `OUTPUT=...`, install with `DESTDIR`, and feature matrix builds with/without libbfd/readline/flex/bison. Generated parser rebuilds should be tested after touching `bpf_exp.l` or `bpf_exp.y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/Makefile -->
