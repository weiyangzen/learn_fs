# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/pmu.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/pmu.h

Purpose: LoongArch PMU helper definitions for KVM selftests. It defines PMU event, counter, CSR, and interrupt constants used to validate virtual PMU behavior.

Important APIs/types/functions: includes LoongArch PMU CSR/event constants, counter selectors, overflow/interrupt bits, and helper declarations used by PMU tests.

Control flow and state: guest PMU tests program event counters through LoongArch CSRs, enable PMU interrupts, execute workload, then inspect counter and interrupt state. Persistent state is per-vCPU virtual PMU state maintained by KVM.

Dependencies and integration: depends on `loongarch/processor.h` CSR access macros and common KVM test assertion infrastructure. It integrates with PMU selftests and timer/interrupt helpers for PMI delivery.

Risks: PMU event encodings and interrupt bits are architecture-specific and host-capability-sensitive. Tests must gate on PMU availability and avoid assuming exact counter increments for events with implementation-defined behavior.

Test signals: LoongArch PMU selftests should catch wrong counter virtualization, missing PMU interrupt delivery, or stale CSR definitions.
