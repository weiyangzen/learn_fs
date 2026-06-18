<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c

Purpose: ACPI/PCC-backed HiSilicon uncore frequency scaling driver. It discovers firmware-supported uncore frequencies, registers dynamic OPPs, exposes related CPUs, and lets either the OS or platform firmware control uncore frequency through devfreq.

Important APIs and control flow: probe allocates `hisi_uncore_freq`, finds a PCC subspace ID from ACPI `_CRS`, requests and validates the PCC mailbox channel, queries platform frequency count and values, registers dynamic OPPs, queries capabilities, conditionally registers a shared `hisi_platform` governor, marks related CPUs from `related-package` or `related-cluster` properties, and registers a devfreq device. `hisi_uncore_cmd_send()` serializes PCC access, enforces minimum turnaround time, writes command/data to shared memory, rings the mailbox, polls command-complete/error status, copies returned data, and completes tx. `hisi_uncore_target()` sends SET_FREQ in MHz after OPP selection; `hisi_uncore_get_cur_freq()` sends GET_FREQ. The custom `hisi_platform` governor switches firmware mode to platform control on start and OS control on stop while suppressing polling through the IRQ-driven flag.

State and persistence behavior: per-device state stores PCC channel/client, channel ID, last command completion time, PCC mutex, devfreq pointer, related CPU mask, and capability flags. Dynamic OPPs live until devres cleanup. The custom governor has global usage counting protected by `hisi_platform_gov_usage_lock`.

Dependencies and integration points: depends on ACPI resources, PCC mailbox, devfreq/OPP/governor APIs, PM QoS units, CPU topology, device properties, and ACPI ID `HISI04F1`.

Risks and test signals: PCC shared memory ABI, command status polling, and `min_turnaround_time` handling are firmware-sensitive. Global governor registration must stay balanced across multiple devices. Related CPU discovery treats malformed firmware as fatal. The platform governor deliberately marks itself IRQ-driven though no IRQ exists. Test signals include PCC timeout/error handling, dynamic OPP list matching firmware, OS/platform mode transitions on governor start/stop/remove, multiple uncore domains sharing the governor, `related_cpus` sysfs output, and frequency get/set round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/hisi_uncore_freq.c -->
