# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cap_helpers.h

Purpose: declares capability toggling helpers and compatibility constants for BPF-related capabilities.

Important APIs and macros: defines `CAP_PERFMON` and `CAP_BPF` if missing; declares `cap_enable_effective()` and `cap_disable_effective()`.

Control flow: header only.

State and persistence: no header state; implementation changes process capabilities.

Dependencies and integration points: includes Linux types/capability headers and errno.

Risks: fallback numeric constants must match kernel UAPI; old systems may lack the capabilities even if constants compile.

Test signals: compile compatibility on older headers and runtime capability toggling through the C implementation.
