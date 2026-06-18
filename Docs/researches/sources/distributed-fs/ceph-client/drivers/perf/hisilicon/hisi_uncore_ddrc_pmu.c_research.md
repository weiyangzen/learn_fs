# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_ddrc_pmu.c

Purpose: Implements HiSilicon DDR Controller uncore PMUs for three ACPI generations. It supports fixed-counter v1 hardware and programmable v2/v3 hardware through the common uncore framework.

Important APIs, types, and functions: `struct hisi_ddrc_pmu_regs` abstracts generation-specific offsets. `hisi_ddrc_pmu_read/write_counter()`, `hisi_ddrc_pmu_write_evtype()`, `hisi_ddrc_pmu_get_event_idx()`, and control/interrupt helpers populate `hisi_uncore_ddrc_ops`. Device info records counter width, event range, attr groups, and private register layout for v1/v2/v3.

Control flow: ACPI IDs `HISI0233`, `HISI0234`, and `HISI0235` select v1, v2, or v3 info. Probe reads topology and `hisilicon,ch-id`, maps MMIO, reads version, requires `sub_id` for v2+, initializes IRQ, selects attributes/counter bits/check range, names the PMU with SCCL/channel and optional sub-id, adds CPU hotplug, initializes common perf callbacks, and registers the PMU.

State and persistence: State is in common `struct hisi_pmu`; v1 uses fixed register offsets and event ID equals counter index, while v2/v3 use programmable event type and 48-bit counters. No disk persistence.

Dependencies and integration: Uses ACPI/platform resources, device properties, shared HiSilicon uncore framework, perf PMU, CPU hotplug, and namespace import.

Risks and test signals: V1 fixed-counter allocation differs from normal bitmap allocation and must prevent duplicate event/counter use. Version/topology property requirements can cause probe failures. Test each ACPI ID, v1 fixed events, v2/v3 programmable events, interrupt masks/status offsets, naming with sub-id, and CPU migration.
