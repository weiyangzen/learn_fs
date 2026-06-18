# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.c

## Purpose

`uncore.c` is the central Intel uncore perf PMU framework. It registers model-specific and discovery-derived uncore PMUs, handles PCI/MSR/MMIO box lifetime, schedules perf events onto limited counters with constraints, polls counters with hrtimers, manages CPU hotplug migration of package/die collection CPUs, and dispatches platform initialization selected from Intel CPU model tables.

## Important APIs, Types, And Functions

Global state includes `uncore_msr_uncores`, `uncore_pci_uncores`, `uncore_mmio_uncores`, `uncore_pci_driver`, `uncore_pci_sub_driver`, `pci2phy_map_head`, `uncore_extra_pci_dev`, `__uncore_max_dies`, and the package collection `uncore_cpu_mask`.

Exported/shared helpers include `uncore_pcibus_to_dieid()`, `uncore_die_to_segment()`, `uncore_device_to_die()`, `__find_pci2phy_map()`, `uncore_event_show()`, `uncore_pmu_to_box()`, `uncore_msr_read_counter()`, `uncore_mmio_exit_box()`, `uncore_mmio_read_counter()`, `uncore_get_constraint()`, `uncore_put_constraint()`, `uncore_shared_reg_config()`, event lifecycle callbacks (`uncore_pmu_event_*()`), `uncore_perf_event_update()`, and `uncore_get_alias_name()`.

Core internal functions are `uncore_assign_hw_event()`, `uncore_collect_events()`, `uncore_get_event_constraint()`, `uncore_assign_events()`, `uncore_validate_group()`, `uncore_pmu_event_init()`, `uncore_pmu_register()`, `uncore_type_init()`, PCI probe/remove/notify paths, CPU hotplug functions, and `intel_uncore_init()`/`intel_uncore_exit()`.

## Control Flow

Module initialization rejects hypervisors, computes max logical dies, matches the boot CPU against `intel_uncore_match`, optionally runs discovery, and then invokes platform `pci_init`, `cpu_init`, and `mmio_init` callbacks. Each selected uncore type is expanded into PMU instances and per-die box arrays. PCI PMUs are registered when matching devices probe or are discovered; MSR/MMIO PMUs are registered during init and receive per-die boxes from CPU hotplug callbacks.

Event initialization validates type, registration, no sampling, valid target CPU, fixed/free-running/generic config rules, optional hardware config hooks, and group schedulability. Adding a non-free-running event collects currently active events, assigns counter indexes using constraints and `perf_assign_events()`, stops/reprograms moved events, then starts new ones if requested. Free-running events are mapped directly to their read-only counter and tracked on `active_list`.

Counters are polled by per-box hrtimers because uncore overflow interrupts are unavailable or unreliable on important platforms. The hrtimer updates active-list free-running events and bitmask-tracked programmable counters, then forwards itself while active.

## State And Persistence Behavior

State is in dynamically allocated `intel_uncore_pmu` arrays, per-die `intel_uncore_box` objects, shared extra-register refcounts/configs, PCI bus-to-die maps, PMU registration flags, event `hw` fields, and hrtimer state. Counts accumulate in `perf_event.count`; raw hardware state lives in MSR, PCI config, or MMIO registers. No durable state is written. CPU hotplug migrates PMU contexts from an outgoing die collection CPU to another CPU in the same die mask and cancels hrtimers before migration.

## Dependencies And Integration Points

This file integrates with Linux perf PMU registration, PCI driver/probe/notifier APIs, x86 CPU model matching, topology and NUMA helpers, hrtimers, raw spinlocks, Intel uncore platform files, and `uncore_discovery.c`. Sysfs integration is via PMU names, `cpumask`, `format`, and `events` attribute groups. Platform descriptions in `uncore_snb.c`, `uncore_nhmex.c`, and other uncore files fill in `intel_uncore_type` arrays consumed here.

## Risks And Edge Cases

Counter scheduling must honor fixed, free-running, and shared-register constraints or perf groups can produce incorrect counts. PCI-to-die mapping depends on platform data and NUMA/topology availability. Hotplug migration can race with hrtimer updates if box CPU ownership is mishandled. Generic discovery PMUs may be absent or partially discovered, so init treats PCI, CPU/MSR, and MMIO paths independently and succeeds if at least one path works. Free-running counters are read-only and must never be programmed like normal counters.

## Test Signals

Signals include module init on supported and unsupported CPUs, sysfs PMU/event/format/cpumask visibility, perf group validation with constrained events, fixed and free-running counter reads, CPU hotplug migration tests, PCI device add/remove tests, lockdep for shared registers, and comparing memory-controller bandwidth events against known traffic.
