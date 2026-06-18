# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_hha_pmu.c

Purpose: Implements the HiSilicon Hydra Home Agent uncore PMU for v1/v2 hardware. It exposes HHA request, snoop, DDR, retry, and cycle events, with optional v2 filters for source ID, trace tag, and data source socket.

Important APIs, types, and functions: Filter extractors decode `srcid_cmd`, `srcid_msk`, `tracetag_en`, and `datasrc_skt`. HHA ops implement packed event-type programming, counter read/write, global and per-counter enable, interrupt mask/status/clear, and filter enable/disable hooks. Probe helpers read topology, support legacy `_UID` as fallback index, map MMIO, read `HHA_VERSION`, select v1/v2 metadata, and register with the common uncore framework.

Control flow: ACPI IDs `HISI0243` and `HISI0244` bind the driver. Probe validates SCCL and index ID, maps resources, initializes IRQ, chooses 16 48-bit v1 counters or eight 64-bit v2 counters, names the PMU `hisi_sccl%d_hha%d`, adds CPU hotplug, initializes common perf callbacks, and registers perf. The common start/stop paths call HHA-specific filter hooks around counter programming.

State and persistence: Runtime state is in `struct hisi_pmu` and HHA MMIO. Filter registers are shared at PMU level, so enable/disable hooks must clear only fields that were requested by the event.

Dependencies and integration: Depends on ACPI, platform MMIO/IRQ, common HiSilicon uncore helpers, CPU hotplug, perf PMU APIs, and sysfs attribute groups.

Risks and test signals: Shared filter fields can conflict when multiple events request different source/data filters. Legacy `_UID` fallback must be verified on older firmware. Test v1/v2 event visibility, filter sysfs formats, source-ID masking, interrupt-driven overflow accounting, and CPU hotplug migration.
