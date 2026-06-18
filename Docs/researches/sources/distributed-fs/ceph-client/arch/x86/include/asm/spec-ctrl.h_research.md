<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h

Purpose: declares x86 speculative-execution control helpers and state used for Spectre/MDS/SSB/IBRS-style mitigations. Important APIs include speculation MSR update helpers, `x86_spec_ctrl_*` state declarations, and entry/exit or context-switch mitigation hooks.

Control flow: CPU feature setup initializes mitigation MSR defaults; context-switch and entry paths update SPEC_CTRL or related MSRs based on task flags and CPU vulnerability state. State includes per-CPU/global shadow values for speculation-control MSRs and task thread flags.

Dependencies include MSR access, CPU bug flags, static keys, thread_info flags, entry code, KVM, and mitigation command-line handling. Risks include missing barriers, stale MSR shadow state, high context-switch overhead, and security regressions. Test signals include Spectre/MDS mitigation selftests, sysfs vulnerability output, context-switch tracing, KVM guest/host tests, and CPU vendor matrix coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h -->
