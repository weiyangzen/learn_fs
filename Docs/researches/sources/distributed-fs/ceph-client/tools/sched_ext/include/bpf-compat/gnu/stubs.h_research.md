# sources/distributed-fs/ceph-client/tools/sched_ext/include/bpf-compat/gnu/stubs.h

Purpose: dummy `gnu/stubs.h` used only during BPF compilation to avoid accidental inclusion of glibc architecture stubs that may require missing 32-bit development headers.

Important APIs/functions: no symbols or declarations; the file intentionally provides an empty compatibility header.

Control flow: none.

State and persistence: none.

Dependencies and integration: placed before system include directories by `BPF_CFLAGS` in the sched_ext Makefile. It intercepts `/usr/include/gnu/stubs.h` when clang compiles `-target bpf` and `__x86_64__` is not defined.

Risks: it is safe only because the real glibc stubs content is irrelevant to these BPF programs. If future included headers genuinely depend on glibc stubs declarations, this shim could mask a real requirement.

Test signals: BPF builds on x86 systems without 32-bit glibc-devel installed should pass; removing this file should reproduce the missing `stubs-32.h` class of failure.
