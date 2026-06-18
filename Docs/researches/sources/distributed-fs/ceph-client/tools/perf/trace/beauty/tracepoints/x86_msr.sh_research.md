# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/tracepoints/x86_msr.sh

Purpose: Generates selected x86 MSR lookup arrays.

Important APIs/types/functions: It emits `x86_MSRs[]`, `x86_64_specific_MSRs_offset`, `x86_64_specific_MSRs[]`, `x86_AMD_V_KVM_MSRs_offset`, and `x86_AMD_V_KVM_MSRs[]`.

Control flow: The first pass captures `MSR_*` values in the `0x00000...` range with exclusions for clashing/noisy entries. The second pass captures `0xc0000...` x86-64-specific values and excludes `K6_WHCR`. The third captures `0xc0010...` AMD-V/KVM values. Offset tables use the lowest matching value as the base.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `x86_msr.c`.

Risks: Coverage is intentionally partial for simple arrays. New ranges need new generated arrays or a different data structure.

Test signals: Regenerate against `msr-index.h`, compile, and verify names from all three ranges.
