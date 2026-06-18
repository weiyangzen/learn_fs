# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bpf.mk

Purpose: Shared make rules for building BPF object files and a local libbpf for networking selftests.

Important APIs/types/functions: Defines `CLANG`, `SCRATCH_DIR`, `BUILD_DIR`, `BPFDIR`, `APIDIR`, include paths, `BPFOBJ`, `MAKE_DIRS`, `get_sys_includes`, `CLANG_TARGET_ARCH`, `CLANG_SYS_INCLUDES`, `BPF_PROG_OBJS`, pattern rule for `$(OUTPUT)/%.o`, libbpf build rule, and `EXTRA_CLEAN`.

Control flow: It creates build directories, extracts host compiler include paths with `clang -v -E` and adds them as `-idirafter` for BPF target builds, handles cross-compile clang target selection, builds all `*.bpf.c` files into BPF ELF objects, and builds/installs libbpf headers into scratch output first.

State and persistence behavior: Writes generated BPF objects and scratch libbpf build/install output under `$(OUTPUT)/tools`. `EXTRA_CLEAN` removes scratch state.

Dependencies and integration points: Included by net Makefile. Requires clang with BPF target support, kernel UAPI headers, tools/lib/bpf, and make.

Risks: Host include extraction is shell/clang-output dependent. Cross-compilation target inference from `CROSS_COMPILE` is simple. RISC-V handling injects `__riscv_xlen`/`__BITS_PER_LONG` macros from clang preprocessing.

Test signals: Successful `BPF_PROG` and `MAKE libbpf` build lines and resulting `$(OUTPUT)/*.o` files indicate BPF selftest objects are available.
