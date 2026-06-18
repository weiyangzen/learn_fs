## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cfi.h

Purpose: minimal arm64 Control Flow Integrity hook header.

Important APIs/types/functions: defines `__bpfcall` as empty, allowing common CFI/BPF code to refer to an architecture calling convention marker.

Control flow: none.

State and persistence: no state.

Dependencies and integration: consumed by BPF and CFI build paths when annotating indirect-call interfaces.

Risks: the empty definition is deliberate; changing it can affect ABI annotations or compiler CFI assumptions. Test signals are CFI-enabled arm64 builds and BPF verifier/JIT selftests.
