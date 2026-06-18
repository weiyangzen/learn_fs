# sources/distributed-fs/ceph-client/samples/bpf/gnu/stubs.h

Purpose: placeholder header to satisfy include resolution for BPF sample builds that encounter `<gnu/stubs.h>`.

Important APIs/types/functions: contains no declarations.

Control flow: no control flow.

State and persistence: no state.

Dependencies and integration: used as an include-path shim when compiling BPF programs in an environment where glibc stubs would otherwise be inappropriate or unavailable.

Risks: because it is empty, any code genuinely requiring glibc stub definitions would compile incorrectly; in these samples it is intended only to satisfy incidental includes.

Test signals: BPF sample compilation succeeds on systems that otherwise report missing `gnu/stubs.h`.
