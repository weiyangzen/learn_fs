<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c

## Purpose
Auxiliary driver for Intel TPMI Performance Limit Reasons. It exposes die-level and CPU-level throttling reason bits through debugfs and allows clearing them.

## Important APIs, Types, And Functions
`struct tpmi_plr` tracks debugfs root, die array, auxiliary device, notifier, and lock. `struct tpmi_plr_die` stores an MMIO base, package/die IDs, and mailbox lock. `plr_read_cpu_status()` and `plr_clear_cpu_status()` use the PLR mailbox with punit core numbers and poll `PLR_RUN_BUSY`. `plr_status_show()` prints die-level and per-CPU reason names. `plr_status_write()` accepts only boolean false/0 to clear status.

## Control Flow
Probe obtains TPMI platform data, TPMI debugfs parent, and MMIO resources, registers a TPMI notifier, maps each resource as one die/domain, creates `plr/domainN/status` for valid headers, and stores drvdata. Reads list die-level `cpus` reasons, then iterate `nr_cpu_ids` filtering by package and power-domain ID before mailbox reads. Writes clear die-level and all matching CPU statuses.

## State And Persistence
State includes debugfs dentries, mapped MMIO resources, mailbox locks, package/die IDs, and notifier registration. Hardware status bits persist until cleared through debugfs.

## Dependencies And Integration Points
Depends on auxiliary bus, Intel VSEC/TPMI APIs, TPMI power-domain helpers, debugfs, MMIO polling, topology, and notifier callbacks for `TPMI_CORE_EXIT`.

## Risks And Test Signals
Risks include mailbox timeout, stale debugfs during TPMI core teardown, CPU iteration over offline/unmapped CPUs, and write ABI accepting only zero. Test debugfs output per domain, clearing behavior, timeout handling, hotplug/power-domain mappings, and TPMI core unload notifier behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c -->
