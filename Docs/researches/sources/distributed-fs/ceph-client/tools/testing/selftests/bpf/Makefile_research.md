# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/Makefile

## Purpose

This large Makefile builds the BPF selftest suite, BPF test runners, helper libraries, generated skeletons, kernel modules, bpftool, benchmark binary, and install/clean targets.

## Important APIs, Types, and Functions

Key variables include `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_KMODS`, `BPFOBJ`, `BPFTOOL`, `VMLINUX_BTF`, `BPF_CFLAGS`, and the `DEFINE_TEST_RUNNER`/`DEFINE_TEST_RUNNER_RULES` make macros. Custom rules generate `vmlinux.h`, compile BPF objects with clang or bpf-gcc, generate skeleton/subskeleton/light-skeleton headers, build `test_progs` flavors, build `test_maps`, `test_verifier`, XDP/XSK utilities, and link `bench`.

## Control Flow and Data Flow

Make first resolves tool paths, feature flags, CFLAGS/LDFLAGS, optional LLVM/libpcap/libcrypto support, and output directories. It builds libbpf and host/cross bpftool, dumps BTF into `vmlinux.h`, compiles BPF programs from `progs/`, generates skeleton headers with bpftool, compiles C test objects, links runners, and copies/install artifacts through kselftest rules. The benchmark target links `bench.o`, helper objects, and every `benchs/bench_*.o`.

## State and Persistence Behavior

Build state lives in `$(OUTPUT)`, scratch tool directories, generated headers, `.d` dependencies, BPF objects, skeleton headers, signed light skeleton material, and copied install subdirectories. `EXTRA_CLEAN` removes these generated artifacts.

## Dependencies and Integration Points

The Makefile integrates with kernel tools build includes, kselftest `lib.mk`, libbpf, bpftool, clang, optional bpf-gcc, LLVM disassembler support, libelf/zlib/pthread/rt, libpcap, cgroup helpers, kernel BTF, and test kernel modules.

## Risks and Edge Cases

Feature detection is sensitive to cross-build output paths, `VMLINUX_BTF` availability, clang target include paths, endian selection, and make version behavior. Skeleton generation intentionally relinks multiple times and diffs outputs to catch non-determinism. Static linking is filtered for shared urandom helper builds. Missing BTF is a hard error.

## Test Signals

Successful `make -C tools/testing/selftests/bpf` builds test runners, BPF objects, skeleton headers, bpftool, modules, docs unless skipped, and `bench`. Failures often identify missing BTF, clang/bpftool/libbpf breakage, skeleton generation drift, or helper library link issues.
