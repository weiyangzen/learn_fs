# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_stx_ldx.c

Purpose: verifies that load/store instruction register fields reject register numbers outside the valid eBPF range.

Important APIs/types/functions: uses raw `BPF_STX`, `BPF_ST`, and `BPF_LDX` encodings with invalid source or destination register IDs such as `R15`, `R14`, `R12`, and `R11`.

Control flow: each case emits one invalid memory instruction followed by exit. Rejection should happen during instruction validation.

State and persistence behavior: no persistent state; validates decoder/register-number state before memory safety analysis.

Dependencies and integration points: generic verifier selftest entries.

Risks: accepting invalid register encodings can corrupt verifier state arrays or produce backend-specific behavior.

Test signals: all reject with exact diagnostics `R15 is invalid`, `R14 is invalid`, `R12 is invalid`, or `R11 is invalid`.
