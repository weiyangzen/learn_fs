# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/debug_print.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/debug_print.h

Purpose: s390 guest debug-print support for KVM selftests. It provides low-level routines/macros to emit guest-visible diagnostic text, typically through s390-specific debug facilities.

Important APIs/types/functions: exposes debug printing helpers and formatting entry points used from guest code, backed by s390 diagnose or console-like mechanisms.

Control flow and state: guest code calls the debug print helper when it needs diagnostic output. The helper formats or copies data to an s390-specific output path. State is transient output data; no durable test state is owned by the header.

Dependencies and integration: integrates with s390 processor/facility helpers and common guest assertion/ucall code. It may depend on s390 diagnose behavior provided by KVM.

Risks: debug output paths are often best-effort and may be unavailable depending on host/KVM setup. Tests should not rely on debug text for pass/fail state.

Test signals: s390 guest tests that print diagnostics validate compilation and basic output delivery; failures should not normally affect test correctness unless the helper is part of the tested facility.
