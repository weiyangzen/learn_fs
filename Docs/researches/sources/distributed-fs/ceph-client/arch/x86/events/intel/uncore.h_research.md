# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.h

## Purpose

`uncore.h` is the shared private interface for Intel uncore perf support. It defines uncore PMU type descriptors, PMU instances, physical boxes, operation callbacks, event descriptors, topology helpers, free-running counter encoding, register-address helpers for MSR/PCI/MMIO backends, and prototypes used by platform-specific uncore files and generic discovery.

## Important APIs, Types, And Fields

Key structures are `intel_uncore_type`, `intel_uncore_ops`, `intel_uncore_pmu`, `intel_uncore_box`, `intel_uncore_extra_reg`, `uncore_event_desc`, `freerunning_counters`, `intel_uncore_topology`, and `pci2phy_map`. `intel_uncore_type` is the main static or discovery-generated PMU contract: name, counter counts/widths, register offsets, masks, constraints, callbacks, attributes, topology mapping, and PMU arrays. `intel_uncore_box` is the live per-die/per-PMU hardware instance with active events, constraints, PCI/MMIO handles, hrtimer, and shared extra registers.

Important inline helpers classify counter indexes (`uncore_pmc_fixed()`, `uncore_pmc_freerunning()`), validate MMIO offsets, compute box/control/counter addresses for PCI and MSR backends, decode free-running event config, select backend-specific register helpers, call type operations, initialize/exit boxes, and convert perf events/devices to uncore objects.

Macros such as `DEFINE_UNCORE_FORMAT_ATTR`, `INTEL_UNCORE_EVENT_DESC`, `UNCORE_PCI_DEV_DATA`, and constraint helpers support concise platform tables.

## Control Flow

The header provides inline dispatch used by `uncore.c`: PMU callbacks call into `uncore_enable_event()`, `uncore_disable_event()`, and `uncore_read_counter()`, which dispatch through `intel_uncore_ops`. Register address calculation selects PCI/MMIO paths when `box->pci_dev` or `box->io_addr` is present, otherwise MSR paths are used. Free-running config helpers validate and map `event=0xff,umask>=0x10` encodings into hardware offsets.

## State And Persistence Behavior

The header defines the state containers but does not allocate durable data. Runtime state spans PMU arrays, box arrays, event slots, active masks, per-counter tags, extra-register refcounts, topology mappings, PCI maps, and global uncore arrays declared as externs. All persistence is in memory or hardware registers for the lifetime of the module and perf events.

## Dependencies And Integration Points

It depends on Linux perf, PCI, slab, APIC/topology, Intel family IDs, and non-atomic 64-bit I/O helpers. It links platform files (`uncore_snb.c`, `uncore_nhmex.c`, server uncore files) to `uncore.c` by declaring init hooks and global arrays. It also exports discovery support hooks and ignore-list externs.

## Risks And Edge Cases

Register-offset helpers embed platform assumptions such as paired counter/control spacing, Coffee Lake 8th CBOX special MSR offsets, fixed-counter sharing, and MMIO map sizes. A wrong `intel_uncore_type` field can program the wrong register. Free-running event encoding has a special `0xff` event code shared with fixed counters, so validation must distinguish umask ranges. MMIO offset validation warns once but returns zero counts on invalid offsets.

## Test Signals

High-signal tests are build coverage across all Intel uncore platform files, sysfs `format` correctness, fixed/free-running event validation, register address calculations for representative MSR/PCI/MMIO types, and hotplug/perf group tests that exercise inline dispatch through each backend.
