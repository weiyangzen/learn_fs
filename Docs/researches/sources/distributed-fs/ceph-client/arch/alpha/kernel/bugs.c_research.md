<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c

**Purpose:** Reports Alpha CPU vulnerability status for sysfs based on CPU family.

**Important APIs/types/functions:** `cpu_is_ev6_or_later`, `cpu_show_meltdown`, `cpu_show_spectre_v1`, and `cpu_show_spectre_v2` under `CONFIG_SYSFS`.

**Control flow:** Sysfs vulnerability attribute reads inspect the HWRPB processor type; EV6 through EV69 report `Vulnerable`, older CPUs report `Not affected`.

**State and persistence behavior:** No mutable state; reads boot-time HWRPB CPU descriptor.

**Dependencies and integration points:** Depends on HWRPB structures, Linux CPU sysfs vulnerability plumbing, and CPU type constants.

**Risks:** The status is a coarse family-based report and does not model mitigations. CPU type range mistakes misreport vulnerability files.

**Test signals:** Read `/sys/devices/system/cpu/vulnerabilities/*` on EV5 and EV6+ configs and validate strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c -->
