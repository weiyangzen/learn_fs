# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/Makefile

Purpose: builds the embedded iterator BPF object and generates lightweight skeleton headers for little- and big-endian BPF targets. The source was read as a complete 67-line file.

Important APIs/rules: variables for `CLANG`, `LLC`, `LLVM_STRIP`, bpftool/libbpf paths, output directories, `all`, `big`, `clean`, `iterators.lskel-%.h`, `$(OUTPUT)/%/iterators.bpf.o`, `$(BPFOBJ)`, and `$(DEFAULT_BPFTOOL)`. The skeleton rule runs `bpftool gen skeleton -L`.

Control flow: building `all` generates the little-endian skeleton; building `big` generates the big-endian skeleton. The object rule compiles `iterators.bpf.c` with `--target=bpf -m$*`, strips debug info, and stores per-endian outputs. Libbpf and bootstrap bpftool are built from in-tree tools as prerequisites.

State and persistence: generated `.output` content and skeleton headers persist in the source/build tree until `clean` removes `.output` and `iterators`.

Dependencies/integration: depends on clang/LLVM strip, bpftool bootstrap, libbpf static archive and installed headers, tools UAPI headers, and the preload kernel module including the generated headers.

Risks and edge cases: toolchain mismatch can change embedded BPF/BTF blobs and skeleton API. Big-endian skeleton generation is separate and easy to omit. `clean` removes the output directory and `iterators` path but not necessarily already checked-in skeleton headers depending on invocation context.

Test signals: `make` and `make big` under the iterator directory, reproducibility checks for generated skeletons, clang target support for both endiannesses, and module build consuming both headers.
