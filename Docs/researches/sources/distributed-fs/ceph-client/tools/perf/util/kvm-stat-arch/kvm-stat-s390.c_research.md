<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c

## Purpose

`kvm-stat-s390.c` implements IBM s390 SIE KVM stat decoding, including child tracepoints that refine intercept reasons.

## Important APIs, Types, and Functions

It expands SIE tables from `asm/sie.h`, defines child key extractors for intercepted instruction, SIGP, diagnose, and program-intercept events, lists tracepoints from SIE enter/exit through child handlers, registers `vmexit` ops, skips `"Wait state"`, and exports s390 hook functions.

## Control Flow

Common exit begin/end handles SIE enter/exit. Child events override the key table and key value: instruction intercept decodes the instruction word through `icpt_insn_decoder()`, SIGP reads `order_code`, diagnose reads `code`, and program intercept reads `code`.

## State and Persistence Behavior

Static decode tables come from kernel UAPI. `__cpu_isa_init_s390()` enables support only when `cpuid` contains `"IBM"`, then sets SIE table and ISA label.

## Dependencies and Integration Points

It depends on common KVM stat, evsel field extraction, and s390 SIE UAPI macros. It is selected by `EM_S390`.

## Risks and Edge Cases

Non-IBM cpuid returns `-ENOTSUP`. Child event field names must match tracepoints. Wait-state skip affects report visibility and should stay aligned with user expectations.

## Test Signals

Tests should cover IBM and non-IBM cpuid, SIE intercept decoding, all child event tables, wait-state skipping, and unknown intercept codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-s390.c -->
