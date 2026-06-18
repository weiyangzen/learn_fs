# sources/distributed-fs/ceph-client/samples/bpf/Makefile

Purpose: builds the kernel BPF sample suite, including userspace loaders, classic BPF-style objects, CO-RE `.bpf.c` objects, skeletons, and local libbpf/bpftool dependencies.

Important APIs/types/functions: defines `tprogs-y`, `always-y`, per-target object lists, libbpf and bpftool build locations, `verify_cmds`, `verify_target_bpf`, `vmlinux.h` generation, `syscall_nrs.h` generation, BTF probes, `CLANG_SYS_INCLUDES`, `.bpf.o` compile rules, linked skeleton generation, and legacy `.c` to BPF object pipeline through `clang | opt | llvm-dis | llc`.

Control flow: kbuild first builds libbpf and helper objects, probes LLVM/BTF capabilities, generates `vmlinux.h` when needed, compiles userspace targets with libbpf, compiles BPF programs with either direct `clang --target=bpf` for `.bpf.c` or the legacy LLVM IR pipeline for other BPF C files, and generates skeletons through bpftool for linked BPF objects.

State and persistence: build outputs include sample executables, BPF object files, generated `vmlinux.h`, generated skeleton headers, local `libbpf/` and `bpftool/` directories, `syscall_nrs.h`, and optional BTF-enriched objects.

Dependencies and integration: depends on kernel kbuild, tools/lib/bpf, tools/bpf/bpftool, LLVM tools, pahole for BTF fallback, installed headers, selftest helpers, and architecture-specific target macros.

Risks: toolchain probing is complex and environment-sensitive. Missing `vmlinux` or `VMLINUX_H` blocks CO-RE builds. System include recovery can mask distro-specific header issues. The legacy pipeline depends on LLVM tools agreeing on IR format and BPF backend support.

Test signals: `make M=samples/bpf`, clean rebuilds, cross-compile smoke tests, generated `vmlinux.h` and skeleton presence, and running representative samples such as `sockex1`, `syscall_tp`, `map_perf_test`, and `hbm`.
