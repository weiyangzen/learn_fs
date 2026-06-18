# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_noc_pmu.c

Purpose: Implements the HiSilicon NoC uncore PMU for network-on-chip flow, buffer, failure, and cycle events.

Important APIs, types, and functions: `struct hisi_noc_pmu_regs` stores register offsets. Filter extractors decode channel (`ch`) and global trace-tag enable (`tt_en`). Ops implement event type programming, four 64-bit counters, counter enable/disable, no-op interrupt mask hooks, global PMU start/stop, overflow status clear, and channel/global trace-tag filter hooks.

Control flow: ACPI ID `HISI04E0` binds v1 metadata. Probe reads SCL, index, and sub-id topology, maps MMIO, selects metadata, reads version, adds CPU hotplug with devm cleanup, initializes the common PMU, names it `hisi_scl%d_noc%d_%d`, registers perf, and installs devm unregister cleanup. Event allocation rejects a new event when its global trace-tag setting conflicts with currently scheduled events.

State and persistence: State is common `struct hisi_pmu`; channel selection is per counter, while trace-tag filtering is global and only cleared when the last counter stops. The hardware has no supported interrupt masking, but overflow status is still read/cleared by common paths if used.

Dependencies and integration: Uses ACPI/platform matching, common HiSilicon uncore framework, perf sysfs groups, CPU hotplug, and devm cleanup.

Risks and test signals: Global trace-tag state can affect all active counters, making group compatibility critical. Channel 0 resets counter value, so default channel 7 is used when unspecified. Test channel defaulting, trace-tag conflict rejection, PMU start/stop, overflow status clearing, and devm cleanup.
