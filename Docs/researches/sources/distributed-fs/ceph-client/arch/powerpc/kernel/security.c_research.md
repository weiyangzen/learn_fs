# sources/distributed-fs/ceph-client/arch/powerpc/kernel/security.c

Purpose: PowerPC CPU vulnerability mitigation control and reporting for Spectre v1/v2, store-forwarding/speculative store bypass, Meltdown/L1TF-like L1D exposure, branch/cache flushes, and user access/RFI/entry flush fixups.

Important APIs/types/functions: global `powerpc_security_features`, `setup_barrier_nospec()`, `setup_spectre_v2()`, CPU vulnerability show callbacks (`cpu_show_meltdown()`, `cpu_show_spectre_v1()`, `cpu_show_spectre_v2()`, `cpu_show_spec_store_bypass()`), `setup_stf_barrier()`, `arch_prctl_spec_ctrl_get()`, `setup_count_cache_flush()`, `setup_rfi_flush()`, `setup_entry_flush()`, `setup_uaccess_flush()`, `rfi_flush_enable()`, `uaccess_flush_key`, and debugfs setters/getters for mitigation toggles.

Control flow: early boot params such as `nospectre_v1`, `nospectre_v2`, `no_stf_barrier`, `spec_store_bypass_disable=`, `no_rfi_flush`, `no_entry_flush`, `no_uaccess_flush`, and `nopti` set disable flags. Setup functions combine those flags with `cpu_mitigations_off()` and firmware/CPU feature bits to patch instruction sites (`do_*_fixups()`), enable static keys, allocate fallback flush memory, and update global state booleans. Branch-cache setup selects none/software/hardware count-cache and link-stack flushes, patching context-switch and KVM guest-exit sites accordingly. Sysfs show methods summarize the resulting vulnerability state; debugfs files can toggle several mitigations at runtime.

State and persistence: mitigation state is stored in global booleans/enums and patched kernel text. Fallback L1D flush memory is allocated from memblock and installed in each PACA. `powerpc_security_features` is read-mostly and exported through debugfs for diagnostics.

Dependencies and integration points: depends on firmware security-feature discovery, CPU feature tables, text patching, PACA/cache metadata, KVM Book3S HV patch sites, debugfs, sysfs CPU vulnerability attributes, `prctl()` speculation-control reporting, and setup code calling mitigation setup after CPU/firmware discovery.

Risks: mitigations are architecture- and firmware-feature sensitive; wrong feature bits can leave systems vulnerable or impose unnecessary overhead. Runtime debugfs toggles patch live kernel text and must maintain instruction ordering. Fallback L1D flush allocation depends on correct L1D size and low bolted/RMA memory. Some mitigations cannot be fully disabled when controlled by firmware or hardware. The `unsafe` debugfs files are powerful and should remain root-only.

Test signals: boot matrix with mitigation-on/off command lines, check `/sys/devices/system/cpu/vulnerabilities/*`, debugfs toggles, static key state for uaccess flush, KVM guest-exit patch behavior, fallback flush allocation under hash/radix modes, and microbenchmarks/regression tests for context-switch and syscall paths.
