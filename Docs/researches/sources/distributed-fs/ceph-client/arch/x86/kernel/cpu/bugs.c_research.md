# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bugs.c

## Purpose
`bugs.c` is the x86 speculative-execution and CPU-vulnerability mitigation coordinator. It selects, updates, applies, and reports mitigations for Spectre v1/v2, Spectre BHI, Retbleed, SRSO, ITS, TSA, VMSCAPE, SSB, L1TF, MDS, TAA, MMIO stale data, RFDS, SRBDS, GDS, iTLB multihit, old microcode, and related SMT-sensitive cases. It is intentionally centralized because many mitigations share MSRs, static keys, return thunks, VERW clearing, IBPB/STIBP policy, SMT policy, KVM exposure, and `/sys/devices/system/cpu/vulnerabilities/*` output.

## Important APIs, Types, and Functions
Key exported/shared state includes `x86_spec_ctrl_base`, per-CPU `x86_spec_ctrl_current`, per-CPU `x86_ibpb_exit_to_user`, `x86_pred_cmd`, `x86_return_thunk`, `switch_to_cond_stibp`, `switch_mm_cond_ibpb`, `switch_mm_always_ibpb`, `switch_vcpu_ibpb`, `cpu_buf_idle_clear`, and `switch_mm_cond_l1d_flush`. KVM-visible exports include `x86_virt_spec_ctrl()`, `switch_vcpu_ibpb`, `itlb_multihit_kvm_mitigation`, `l1tf_mitigation`, `l1tf_vmx_mitigation`, and `gds_ucode_mitigated()`.

The file follows a common pattern for each vulnerability: `<vuln>_select_mitigation()` chooses a mode from CPU bug flags, boot parameters, compile-time config, attack-vector controls, and hardware support; optional `<vuln>_update_mitigation()` resolves cross-mitigation dependencies; `<vuln>_apply_mitigation()` mutates CPU caps, MSRs, static keys, SMT state, or thunks. `cpu_select_mitigations()` is the top-level boot orchestrator. `cpu_bugs_smt_update()` reacts to SMT state changes after boot.

Important runtime APIs are `update_spec_ctrl_cond()`, `spec_ctrl_current()`, `x86_spec_ctrl_setup_ap()`, `arch_prctl_spec_ctrl_set()`, `arch_prctl_spec_ctrl_get()`, and `arch_seccomp_spec_mitigate()`. These connect the boot-selected policy to context switch, seccomp, prctl, vCPU load, AP startup, and return-to-user paths.

## Control Flow
Early boot parameter handlers seed mode globals before mitigation selection. `cpu_select_mitigations()` first reads `MSR_IA32_SPEC_CTRL` into `x86_spec_ctrl_base`, clears inherited mitigation bits from kexec, reads `MSR_IA32_ARCH_CAPABILITIES`, and prints active attack-vector policy. It then runs all selection functions before alternatives are patched, runs update functions in dependency order, then applies each mitigation. Ordering matters: Spectre v2 selection feeds Retbleed, ITS, BHI, and Spectre v2 user handling; Retbleed can force Spectre v2 user STIBP behavior and can satisfy SRSO/VMSCAPE IBPB needs; MDS/TAA/MMIO/RFDS share `verw_clear_cpu_buf_mitigation_selected`.

`cpu_bugs_smt_update()` is invoked when SMT state changes. It updates STIBP static keys or `SPEC_CTRL_STIBP`, toggles buffer clearing for MDS/TSA cases, and emits one-time warnings when SMT leaves a selected mitigation incomplete.

`arch_prctl_spec_ctrl_set()` and `arch_prctl_spec_ctrl_get()` route `PR_SPEC_STORE_BYPASS`, `PR_SPEC_INDIRECT_BRANCH`, and `PR_SPEC_L1D_FLUSH` to per-task flag handlers. Current-task updates immediately call speculation-control update paths; non-current task changes are delayed until scheduling.

## State and Persistence
Most mitigation decisions are `__ro_after_init` globals. Runtime mutable state is deliberately narrow: per-CPU cached SPEC_CTRL values, per-task speculation flags, static keys for context-switch and idle paths, KVM-visible globals, and SMT-dependent STIBP/buffer-clear adjustments. MSR state persists per CPU until changed, so AP startup calls `x86_spec_ctrl_setup_ap()`, `update_srbds_msr()`, and `update_gds_msr()` from the CPU bring-up path in `common.c`.

Sysfs vulnerability output is generated from the selected globals and current SMT/static-key state. These files are observations of kernel state, not stored configuration.

## Dependencies and Integration Points
This file depends on CPU bug bits from `common.c`, capability clearing/forcing from `cpuid-deps.c`, CPU attack-vector controls, SMT scheduling state, BPF unprivileged state, KVM headers, x86 MSR helpers, return thunk symbols, alternatives/static keys, x86 FPU/entry flags, E820 memory ranges for L1TF, and hypervisor detection. It integrates with process APIs through `prctl` and seccomp, with KVM through exported mitigation variables/functions, with CPU hotplug through AP setup and SMT update callbacks, and with sysfs through `cpu_show_*()` vulnerability attributes.

## Risks
The main risk is ordering: moving select/update/apply calls can leave related mitigations inconsistent, for example STIBP mode before Retbleed resolution, ITS before Spectre v2 retpoline mode, or VERW state before MDS/TAA/MMIO/RFDS updates. MSR writes must preserve reserved bits via `x86_spec_ctrl_base`. Static keys must only be enabled when the entry/context-switch code has matching alternatives. SMT warnings and disablement must not over-disable systems unless a selected mode explicitly asks for `nosmt` or global SMT mitigation policy requires it. Sysfs strings are ABI-like and are used by tests and admin tooling.

## Test Signals
Useful validation signals are boot logs with `mitigations:` and per-vulnerability prefixes, `/sys/devices/system/cpu/vulnerabilities/*` contents, `prctl(PR_SET_SPECULATION_CTRL/PR_GET_SPECULATION_CTRL)` behavior for SSB, indirect branch, and L1D flush, CPU hotplug/AP bring-up on affected hardware, KVM module behavior for exported mitigation state, unprivileged eBPF warnings, SMT on/off transitions, and command-line matrix tests for each early parameter.
