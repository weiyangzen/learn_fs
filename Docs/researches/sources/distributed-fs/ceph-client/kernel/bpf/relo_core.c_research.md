# sources/distributed-fs/ceph-client/kernel/bpf/relo_core.c

Purpose: imports the shared libbpf CO-RE relocation implementation into the kernel BPF tree by including `../../tools/lib/bpf/relo_core.c`. The source was read as a complete 2-line file.

Important APIs/functions: this file defines no local functions; it compiles the shared `relo_core.c` implementation in the kernel build context. The imported code provides CO-RE relocation logic used for BTF-based field/type relocations.

Control flow: runtime/control flow is entirely in the included libbpf source. This wrapper only selects the implementation at compile time.

State and persistence: no local state. Imported relocation code operates on BTF/relo data supplied by callers.

Dependencies/integration: tightly couples kernel BPF CO-RE support to the in-tree `tools/lib/bpf/relo_core.c` source. Any include-path or API mismatch between kernel and tools code will surface here.

Risks and edge cases: sharing code by textual include can expose kernel builds to assumptions from tools/lib/bpf. Local review must include the imported file for behavioral changes, even though this wrapper is tiny. License tag allows LGPL/BSD dual-licensed imported implementation.

Test signals: CO-RE relocation selftests, BTF relocation verifier tests, kernel build with tools/lib/bpf changes, and compile warnings/errors from included code.
