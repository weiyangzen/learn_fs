# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_perf.c

## Purpose

`book3s_hv_p9_perf.c` isolates POWER9 and later performance monitor state across KVM-HV guest entry and exit. It freezes PMU counters before switching ownership, saves host counters when the host is using the PMU, loads guest counters only when requested or demand-enabled, and restores host counters after guest exit.

## Important APIs, Types, And Functions

The file exports `switch_pmu_to_guest()` and `switch_pmu_to_host()`. The local helper `freeze_pmu()` forces MMCR0/MMCRA into a frozen, non-sampling state, with ARCH_31 handling for `MMCR0_PMCCEXT` and `MMCRA_BHRB_DISABLE`. State is stored in `struct p9_host_os_sprs`, `vcpu->arch.pmc[]`, `vcpu->arch.mmcr[]`, `vcpu->arch.mmcra`, `vcpu->arch.siar`, `vcpu->arch.sdar`, and `vcpu->arch.sier[]`.

## Control Flow

On guest entry, `switch_pmu_to_guest()` checks the pinned VPA/lppaca `pmcregs_in_use` flag to decide whether the guest requested PMU preservation. If the host currently uses the PMU (`ppc_get_pmu_inuse()`), it saves host MMCR0/MMCRA, freezes the PMU, and then saves all PMCs, MMCR1/MMCR2, SDAR, SIAR, SIER, and ARCH_31 MMCR3/SIER2/SIER3. On pseries it mirrors the selected PMU ownership into the host lppaca `pmcregs_in_use`. It loads guest PMU registers when `load_pmu` is true or HFSCR[PM] is already enabled from a previous PMU facility fault, writing MMCRA before MMCR0 last. For non-nested guests it sets HFSCR[PM] when the PM facility is permitted.

On guest exit, `switch_pmu_to_host()` again checks guest VPA `pmcregs_in_use`, with an optional nested PMU workaround that forces saving for nesting-capable guests. If saving is required, it captures guest MMCR0/MMCRA, freezes counters, and saves the full PMU state into `vcpu->arch`. If saving is not requested but HFSCR[PM] is set, it freezes whatever the guest touched and clears HFSCR[PM] for non-nested guests to demand-fault future access. It then restores pseries host lppaca PMU ownership and, if the host uses PMU, reloads host PMC/MMCR/SIAR/SDAR/SIER state and finally MMCRA/MMCR0.

## State And Persistence Behavior

Guest PMU state persists only when the guest declares PMU use or the nested workaround requires it. Otherwise KVM uses HFSCR[PM] demand faulting to avoid saving every counter on every exit. Host PMU state is transiently stored in `p9_host_os_sprs` across the entry call. The pseries lppaca PMU-use flag is updated on both sides so the parent environment sees accurate PMU ownership.

## Dependencies And Integration Points

This file is called directly by `kvmhv_vcpu_entry_p9()` before and after `kvmppc_p9_enter_guest()`. It depends on `asm/pmc.h`, SPR accessors, CPU feature bits, lppaca/VPA state, HFSCR[PM], pseries detection through `kvmhv_on_pseries()`, and the optional `CONFIG_KVM_BOOK3S_HV_NESTED_PMU_WORKAROUND`.

## Risks

Risk centers on counter leakage, lost PMU alerts, and nested guest accounting. Loading guest PMU state when not needed wastes time, but failing to save when needed loses guest-visible counter values. Freezing must happen before reading counters to avoid races. The nested workaround exists because older L1s may mishandle `pmcregs_in_use`; removing or changing it can regress nested PMU correctness. ARCH_31 BHRB and extended counter controls must stay aligned with hardware behavior.

## Test Signals

Useful tests include guests that never use PMU, guests that set lppaca `pmcregs_in_use`, guests that touch PMU registers without declaring use and fault through HFSCR[PM], host perf running while a guest runs, nested PMU workloads, and POWER10/POWER11 systems covering MMCR3 and SIER2/SIER3 save/restore.
