# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/gnu/stubs.h

Purpose: dummy header to satisfy glibc `features.h` include expectations when compiling with `clang --target=bpf`.

Important APIs and functions: no APIs; contains only a comment.

Control flow: none.

State and persistence: none.

Dependencies and integration points: used through include path layout so BPF-target compilation can find `gnu/stubs.h`.

Risks: intentionally empty; if a build unexpectedly needs real glibc stubs, this only masks include resolution and not ABI support.

Test signals: successful BPF-target compilation where system headers include `gnu/stubs.h`.
