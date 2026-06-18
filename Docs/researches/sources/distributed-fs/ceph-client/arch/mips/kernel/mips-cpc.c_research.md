<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c

### Purpose
`mips-cpc.c` probes and maps the MIPS Cluster Power Controller and serializes redirected CPC core access on older CM revisions.

### Important APIs, Types, And Functions
The exported state is `mips_cpc_base`. Important functions are `mips_cpc_default_phys_base()`, `mips_cpc_probe()`, `mips_cpc_lock_other()`, and `mips_cpc_unlock_other()`. The internal `mips_cpc_phys_base()` uses CM GCR CPC status/base registers to locate or enable CPC.

### Control Flow
Default base discovery first looks for a device-tree node compatible with `mti,mips-cpc`. Probe initializes per-CPU locks, obtains a physical base by checking CM presence and CPC existence, leaves an already enabled CPC at its existing base, or enables it at the default DT base, then `ioremap()`s the register space. For CM revisions below CM3, lock/unlock disables preemption, locks the current core's CPC redirect register, writes `CPC_Cx_OTHER_CORENUM`, and barriers before access. CM3+ uses CM-level locking instead, so CPC lock functions return.

### State, Persistence, And Dependencies
State is the mapped CPC base and per-CPU core locks/IRQ flags. CPC enablement persists in GCR CPC base registers. Dependencies include device tree address parsing, CM probe helpers, bitfield macros, CPC register accessors, and CPU core numbering.

### Integration Points
The CPC is used by MIPS CPS CPU power, idle, and hotplug paths. Its locking complements `mips_cm_lock_other()` for register spaces that expose an "other core" selector.

### Risks
Probe requires a working CM mapping. Missing or wrong DT address prevents enabling CPC. On older CM revisions, failing to serialize `CPC_CL_OTHER` can race with other VPEs and redirect register operations to the wrong core.

### Test Signals
Boot DT and non-DT CPC systems, confirm CPC enable bit/base, exercise CPU hotplug or power-state operations, and stress parallel cross-core CPC access on CM2-era hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c -->
