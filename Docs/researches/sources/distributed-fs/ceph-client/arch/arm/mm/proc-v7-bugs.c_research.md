# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-bugs.c

## Purpose
This file initializes ARMv7 CPU vulnerability mitigations for Spectre v2 and Spectre BHB, choosing branch predictor hardening, firmware calls, vector updates, and CPU-specific auxiliary-control checks.

## Important APIs, Types, and Functions
`spectre_v2_get_cpu_fw_mitigation_state()` queries SMCCC `ARCH_WORKAROUND_1` when PSCI is available. Under `CONFIG_HARDEN_BRANCH_PREDICTOR`, `harden_branch_predictor_fn` stores a per-CPU mitigation function and `spectre_v2_install_workaround()` selects BPIALL, ICIALLU, HVC, or SMC methods, also replacing `cpu_do_switch_mm` for firmware conduits. `cpu_v7_spectre_v2_init()` maps CPU parts to mitigation methods and updates global Spectre state.

For BHB, `spectre_bhb_method`, `spectre_bhb_install_workaround()`, and `cpu_v7_spectre_bhb_init()` select loop, BPIALL, ICIALLU, or firmware-style methods and update vectors through `spectre_bhb_update_vectors()`. Public entry points are `cpu_v7_ca8_ibe()`, `cpu_v7_ca15_ibe()`, and `cpu_v7_bugs_init()`.

## Control Flow
ARMv7 proc-info tables call a bugs-init hook during CPU bring-up. The hook reads CPUID implementor/part, decides whether the CPU is unaffected, locally mitigated, or firmware-dependent, installs per-CPU or global hooks, checks required AUXCR IBE bits for Cortex-A8/A15 paths, updates Spectre state, and logs selected methods.

## State and Persistence Behavior
The file mutates per-CPU `harden_branch_predictor_fn`, global `cpu_do_switch_mm`, BHB vector state, `spectre_bhb_method`, per-CPU warning state, and global Spectre reporting state. These choices persist for the running kernel.

## Dependencies and Integration Points
It depends on SMCCC/PSCI, CP15 system-register helpers, CPU part IDs, SMP per-CPU state, `asm/spectre.h`, `asm/proc-fns.h`, and ARMv7 switch-mm hardening stubs from `proc-v7.S`. It integrates with CPU bring-up, context switching, exception vectors, and sysfs/proc vulnerability reporting.

## Risks
Mitigation selection is security-sensitive. Firmware conduit detection must be correct for Cortex-A57/A72. Mixed CPUs can disagree on BHB method; the code marks the system vulnerable on disagreement. If branch predictor hardening is disabled, affected systems remain vulnerable by configuration. AUXCR checks rely on firmware setting IBE bits.

## Test Signals
Build with and without `CONFIG_ARM_PSCI`, `CONFIG_HARDEN_BRANCH_PREDICTOR`, and `CONFIG_HARDEN_BRANCH_HISTORY`. Boot affected Cortex-A8/A9/A15/A57/A72/A73/A75 and Broadcom Brahma variants where available. Check vulnerability reporting, boot logs for selected methods, SMCCC return handling, CPU hotplug behavior, and that context-switch hardening stubs are used for firmware methods.
