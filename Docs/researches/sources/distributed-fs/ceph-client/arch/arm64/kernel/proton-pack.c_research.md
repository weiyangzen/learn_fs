# sources/distributed-fs/ceph-client/arch/arm64/kernel/proton-pack.c

Purpose: this file detects, reports, and enables ARM64 mitigations for Spectre v1, v2, v3a, v4/SSBD, and Spectre-BHB. It coordinates CPU feature detection, firmware SMCCC calls, vector patching, per-task prctl policy, and sysfs vulnerability strings.

Important APIs and state: global mitigation states include `spectre_v2_state`, `spectre_v4_state`, and `spectre_bhb_state`, updated monotonically by `update_mitigation_state()`. Per-CPU state includes `bp_hardening_data` and `arm64_ssbd_callback_required`. Public hooks include `cpu_show_spectre_v1()`, `cpu_show_spectre_v2()`, `cpu_show_spec_store_bypass()`, `has_spectre_v2()`, `spectre_v2_enable_mitigation()`, `has_spectre_v3a()`, `spectre_v3a_enable_mitigation()`, `has_spectre_v4()`, `spectre_v4_enable_mitigation()`, `spectre_v4_enable_task_mitigation()`, `arch_prctl_spec_ctrl_get/set()`, `is_spectre_bhb_affected()`, `spectre_bhb_enable_mitigation()`, and alternative patch callbacks.

Control flow: boot parameters (`nospectre_v2`, `ssbd=`, `nospectre_bhb`) set policy early. V2 first checks hardware CSV2/safe-list, then firmware workaround 1 and optional CPU-specific link-stack sanitization. V4 checks safelists, SSBS hardware, firmware workaround 2, and per-task prctl state. BHB chooses between ECBHB, ClearBHB instruction, branchy loop, firmware workaround 3, or vulnerability, and selects EL1/KVM hardening vectors. Alternative patch callbacks replace NOP/branch/MOV instructions based on final mitigation choices.

State and integration: mitigation state is global/per-CPU and should not worsen after capabilities finalize. Per-task store-bypass state is stored in task speculation flags and `TIF_SSBD`; context switch code in `process.c` calls `spectre_v4_enable_task_mitigation()`.

Dependencies: SMCCC, CPU MIDR/ftr helpers, alternative patching, vectors, KVM hyp vector slots, BPF sysctl for unprivileged eBPF reporting, and prctl speculation controls.

Risks: mixed big.LITTLE systems can have heterogeneous mitigation support; late CPU onlining after finalized capabilities is guarded. Incorrect vector selection or firmware conduit patching can leave entry paths unmitigated. User-visible prctl policy must respect force-on/off semantics.

Test signals: sysfs vulnerability files, boot logs for disabled mitigations, CPU hotplug with mixed cores, prctl store-bypass tests, BPF warning path, and alternative-patching validation for BHB/SSBD vectors.
