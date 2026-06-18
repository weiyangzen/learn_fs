# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snb.c

## Purpose

`uncore_snb.c` supplies client/platform Intel uncore PMU definitions from Nehalem/Sandy Bridge through newer client parts such as Tiger Lake, Alder/Lunar/Panther/Nova Lake. It defines MSR PMUs for CBOX/ARB/clock/cNCU/SANTA-style units, PCI/MMIO memory-controller PMUs, free-running bandwidth counters, PCI ID tables, and init hooks consumed by `uncore.c`.

## Important APIs, Types, And Functions

Exported hooks include `snb_uncore_cpu_init()`, `nhm_uncore_cpu_init()`, `skl_uncore_cpu_init()`, `icl_uncore_cpu_init()`, `tgl_uncore_cpu_init()`, `adl_uncore_cpu_init()`, `mtl_uncore_cpu_init()`, `lnl_uncore_cpu_init()`, `ptl_uncore_cpu_init()`, `nvl_uncore_cpu_init()`, `tgl_uncore_mmio_init()`, `tgl_l_uncore_mmio_init()`, `adl_uncore_mmio_init()`, `lnl_uncore_mmio_init()`, `ptl_uncore_mmio_init()`, `snb_pci2phy_map_init()`, and PCI init wrappers for SNB/IVB/HSW/BDW/SKL.

Key function families are MSR box/event ops (`snb_uncore_msr_*`, SKL/ADL/MTL/LNL variants), IMC PCI/MMIO initialization (`snb_uncore_imc_init_box()`, `snb_uncore_imc_event_init()`, `uncore_get_box_mmio_addr()`), free-running counter setup for SNB/TGL/ADL IMCs, and discovery-merging for PTL through `uncore_get_uncores()`.

Static `intel_uncore_type` objects define event masks, register bases, counter widths, fixed counters, constraints, format groups, event aliases, and per-generation PMU arrays.

## Control Flow

CPU-model init in `uncore.c` calls the matching hook here. Each hook mutates shared static type descriptors as needed for that generation, then assigns `uncore_msr_uncores`, `uncore_pci_uncores`, `uncore_mmio_uncores`, and/or `uncore_pci_driver`. The common uncore framework later initializes types, registers PMUs, and manages boxes.

Desktop IMC PCI init scans known memory-controller PCI IDs, establishes a bus-to-die map, and selects an appropriate PCI driver. SNB IMC events use a custom PMU `event_init()` to preserve old free-running counter encoding while translating to standard uncore free-running `event=0xff,umask=...` config. TGL/ADL/LNL MMIO paths map IMC or SAFBAR-derived MMIO windows and use generic or custom MMIO ops. PTL/NVL combine discovered MMIO uncores with extra static free-running types and override selected discovered type descriptors by type ID.

## State And Persistence Behavior

Most state is static platform description reused across models and sometimes mutated at init time. Runtime state is allocated by `uncore.c` boxes and PMUs. PCI IMC maps one physical bus to die 0 for client systems. MMIO boxes store `io_addr` mappings freed by common exit callbacks. Free-running counters are always active and are polled by the common hrtimer path.

## Dependencies And Integration Points

This file depends on MSR access, PCI device scanning/config reads, memory-controller BAR layout, generic uncore helpers, discovery helpers for newer platforms, and topology core/CBOX count logic. Userspace sees the result as uncore PMUs with generation-specific `format` and `events` sysfs files.

## Risks And Edge Cases

Risk comes from broad platform coverage and mutable shared descriptors. Init hooks change counter counts, register bases, ops pointers, and PMU arrays based on CPU generation; incorrect ordering can affect later model setup. IMC BARs may be disabled or absent, and fallback device lookup may map wrong or no MMIO region. SNB IMC counters are 32-bit and require `readl()` instead of the generic 64-bit MMIO read. Free-running and fixed counters share the `0xff` event code and need careful umask interpretation.

## Test Signals

Strong signals include boot/sysfs PMU coverage for each supported generation, memory bandwidth sanity tests for PCI and MMIO IMC counters, event-format parsing for SNB/NHM/ADL/LNL masks, CBOX count matching hardware, free-running counter wrap polling, CPU hotplug with active uncore events, and discovery override checks for PTL/NVL type IDs.
