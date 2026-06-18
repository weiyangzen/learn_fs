<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c

### Purpose
`mips-cm.c` probes and manages the MIPS Coherence Manager GCR space. It maps the GCR region, configures default targets and optional L2-only sync space, serializes access to redirected "other" core/VP registers, reports CM errors, and identifies whether the current CPU is the first online CPU in a cluster.

### Important APIs, Types, And Functions
Globals include `mips_gcr_base`, `mips_cm_l2sync_base`, `mips_cm_is64`, and `mips_cm_is_l2_hci_broken`. Important APIs are `mips_cm_phys_base()`, `mips_cm_l2sync_phys_base()`, `mips_cm_update_property()`, `mips_cm_probe()`, `mips_cm_lock_other()`, `mips_cm_unlock_other()`, `mips_cm_error_report()`, and `mips_cps_first_online_in_cluster()`.

### Control Flow
Probe reads CP0 config registers for CMGCRBase support, maps the GCR base, validates the mapped base register, sets the default target to memory, disables CM regions, probes and maps L2-only sync for CM major revision >= 6, computes register width, and initializes per-CPU locks. `mips_cm_lock_other()` disables preemption and locks either per-current-core or per-CPU, writes `GCR_CL_OTHER`, and issues a memory barrier before redirected register access. Error reporting decodes CM2 or CM3 error causes into human-readable fields, prints address/multiplicity registers, then reprimes the cause register.

### State, Persistence, And Dependencies
State lives in mapped GCR registers, per-CPU locks/flags, DT-derived EyeQ6 quirk state, and CPS cluster masks. Dependencies include `asm/mips-cps.h`, CP0 CM registers, bitfield macros, device tree, SMP/CPS support, and spinlocks.

### Integration Points
The file is shared by CPS SMP bring-up, CPC access, cache/coherency error handling, L2 sync users, and platform quirks. `mips-cpc.c` depends on CM presence and revision behavior.

### Risks
Redirected "other" accesses are race-prone without the locks and preemption disable. Misdetecting CM base or width causes invalid MMIO. Error decode tables are revision-specific and can misreport newer hardware if fields change.

### Test Signals
Boot CM2, CM3, and CM3.5+ systems, validate GCR mapping, redirected core/VP access under SMP, CM error injection/logging where available, L2-only sync mapping on revision >= 6, and EyeQ6 device-tree quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c -->
