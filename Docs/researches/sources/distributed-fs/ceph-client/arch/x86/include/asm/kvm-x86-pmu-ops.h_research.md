<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h

## Purpose
KVM x86 PMU operation list header for generating backend PMU callbacks. The header is 33 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
Like kvm-x86-ops.h, it is macro-included to declare required and optional PMU operations for Intel/AMD virtual PMU behavior.

## State and Persistence
State is backend PMU dispatch metadata; actual PMU state is in vCPU PMU structures and hardware MSRs.

## Dependencies and Integration Points
Depends on KVM PMU core, VMX/SVM PMU implementations, perf_event, CPUID model exposure, and macro inclusion conventions.

## Risks
Risks include backend operation mismatch, optional callback default behavior hiding unsupported PMU features, and ABI changes to virtual PMU state.

## Test Signals
Tests should run KVM PMU unit tests, perf in guests, Intel/AMD vPMU configs, migration of PMU state, and disabled-vPMU fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h -->
