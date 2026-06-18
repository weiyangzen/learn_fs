<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/Makefile

## Purpose

Custom sched_ext selftest build system that builds libbpf/bpftool helpers, generates vmlinux.h and BPF skeletons for every .bpf.c scheduler, compiles all C testcase objects, and links a single serial runner.

## Important APIs, Types, and Functions

Uses Build.include, Makefile.arch, lib.mk with OVERRIDE_TARGETS, BPFTOOL, VMLINUX_BTF discovery, bpftool gen object/skeleton/subskeleton, clang -target bpf, libbpf.a, auto-test-targets, TEST_GEN_PROGS=runner, and C/BPF flags for sched_ext headers.

## Control Flow and Integration

Build creates output directories, builds libbpf and host bpftool, dumps vmlinux.h from BTF, compiles each BPF program, generates skeleton headers, compiles runner/testcase/util objects, and links runner. Constructors in testcase objects register tests into runner.

## State and Persistence Behavior

Persists build artifacts under $(OUTPUT)/build and generated skeleton headers in the output include dir; clean removes output and runner.

## Dependencies and Integration Points

Requires clang, bpftool, libelf, zlib, zstd, pthreads, BTF vmlinux, tools/lib/bpf, tools/sched_ext headers, and kernel generated headers when available.

## Risks and Edge Cases

BTF path discovery is fragile across build trees. All tests depend on all skeletons by default, so one BPF compile failure blocks the runner. Cross-compile and clang include discovery must stay correct.

## Test Signals

Successful make creates runner; `runner -l` lists auto-test-targets; serial runner execution validates generated skeleton integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/Makefile -->
