<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile

Purpose: this is the main bpftool build system. It builds libbpf for target and bootstrap use, optionally builds BPF skeletons, compiles bpftool objects, links the final bpftool binary, installs bash completion, and delegates documentation targets.

Important targets/variables: `LIBBPF`, `LIBBPF_BOOTSTRAP`, include directories, internal libbpf headers, `BPFTOOL_BOOTSTRAP`, `SRCS`, `OBJS`, `BOOTSTRAP_OBJS`, `VMLINUX_BTF_PATHS`, `BUILD_BPF_SKELS`, and feature flags drive the build. Feature tests cover clang CO-RE, LLVM, libcap, libbfd variants, and libelf zstd. Targets include `all`, `bootstrap`, `clean`, `install-bin`, `install`, `uninstall`, and `doc*`.

Control flow: the Makefile derives `srctree`, creates output directories, builds target libbpf and host bootstrap libbpf, imports internal headers, runs feature detection unless only doc/clean goals are requested, chooses LLVM or libbfd JIT disassembly support, optionally removes `jit_disasm.c` and `sign.c`, generates `vmlinux.h` and skeleton headers with bootstrap bpftool when CO-RE prerequisites are available, compiles `kernel/bpf/disasm.c` as `disasm.o`, and links `bpftool`.

State and persistence: build state is under `$(OUTPUT)` or current directory: target and bootstrap libbpf trees, dependency files, objects, skeleton headers, `vmlinux.h`, feature dumps, and `bpftool`. Install persists the binary under `$(prefix)/sbin` and bash completion under `$(bash_compdir)`.

Dependencies and integration points: it depends on tools libbpf, kernel headers, libelf, zlib, optional zstd, libcap, libcrypto, LLVM/clang/strip, libbfd/opcodes, and a valid vmlinux BTF source for skeleton generation. It integrates with kernel build outputs through `O`, `KBUILD_OUTPUT`, `VMLINUX_BTF`, and `VMLINUX_H`.

Risks: optional feature detection strongly changes compiled command coverage, especially JIT disassembly, signing, libcap permission handling, and skeleton-backed commands. Host and target compiler flag separation must remain correct for cross builds. If no BTF source is found or clang CO-RE is unavailable, skeleton-dependent functionality is compiled out through `BPFTOOL_WITHOUT_SKELETONS`. Unset `OUTPUT` can place many generated files in the source tree.

Test signals: build matrix coverage should include native, cross, `OUTPUT=`, `SKIP_LLVM=1`, `SKIP_LIBBFD=1`, `SKIP_CRYPTO=1`, with/without libcap, with explicit `VMLINUX_H`, and doc/install/uninstall flows. Runtime smoke tests should verify compiled-out feature messaging when optional dependencies are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/Makefile -->
