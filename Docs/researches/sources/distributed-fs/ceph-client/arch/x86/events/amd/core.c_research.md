## sources/distributed-fs/ceph-client/arch/x86/events/amd/core.c

Purpose: AMD core PMU implementation for generic perf events, hardware cache event mappings, constraints, counter programming, overflow handling, branch-stack integration, and KVM virtualization controls.

Important APIs/state: `amd_pmu_init()`, `amd_core_pmu_init()`, `amd_pmu_hw_config()`, `amd_core_hw_config()`, NB constraint helpers, CPU hotplug callbacks, `amd_pmu_handle_irq()`, `amd_pmu_v2_handle_irq()`, `amd_pmu_v2_snapshot_branch_stack()`, event sysfs attributes, `amd_pmu_enable_virt()`, and `amd_pmu_disable_virt()`. Key state includes `x86_pmu`, hardware event maps, `event_offsets/count_offsets`, `amd_pmu_global_cntr_mask`, per-CPU `amd_nb`, and `perf_nmi_tstamp`.

Control flow: init selects event maps by Zen/family, chooses legacy or core PerfCtr MSRs, detects PerfMonV2 global-control/status support, installs constraint callbacks for Fam15h, Fam17h pair events, and Fam19h BRS, then chooses LBR or BRS branch support. Event config handles host/guest exclude bits, precise-event forwarding to IBS, raw masks, pair constraints, and branch-stack setup. IRQ handlers stop counting, read overflow status or top-bit state, update event counts, save branch stacks, signal perf overflow, acknowledge status, and claim latent NMIs within a bounded window.

State/persistence: programs PMU MSRs, global status/control bits, per-CPU active masks/events, NB owner arrays, branch stacks, and virtualization masks exported for KVM.

Integration points: generic x86 perf core, AMD LBR/BRS/IBS/uncore, KVM mediated vPMU, CPU hotplug, sysfs PMU format/events/caps, APIC NMI handling, and hardware cache event translation.

Risks: counter constraints and NB sharing are race-sensitive across cores. NMI latency handling prevents unknown-NMI storms. PerfMonV2 status reserved bits depend on microcode. Test signals include `perf stat/record` on AMD families 15h/17h/19h/Zen4+, branch-stack sampling, CPU hotplug, KVM guest/host exclude tests, NMI stress, sysfs format checks, and IBS precise forwarding.
