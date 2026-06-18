<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c

**Purpose:** `sclp_early.c` consumes early SCLP read-SCP information to populate the global `struct sclp_info sclp`, detect machine facilities, save IPL information, and discover line-mode/VT220 console support before normal drivers are initialized.

**Important APIs and functions:** Exported global `sclp` stores detected capabilities. `sclp_early_detect()` runs facility detection and console detection. `sclp_early_get_ipl_info()` returns saved IPL metadata. `sclp_early_get_core_info()` reads CPU info through early SCLP commands. `sclp_early_adjust_va()` converts the preserved early SCCB pointer to virtual addressing.

**Control flow, state, and persistence:** `sclp_early_facilities_detect()` reads the cached early info SCCB, sets many facility booleans, memory increment size/count, max cores, CPU features of the boot CPU, HSA size, machine type IDs, and load parameter. `sclp_early_detect()` then disables SCLP event notifications and inspects the returned masks to determine available console transports. This state persists in `sclp` for later SCLP users.

**Dependencies and integration:** It depends on early SCLP core helpers, IPL structures, memblock allocation, facility tests, CPU entry layouts, and `sclp_sdias.h` for dump-related integration.

**Risks and test signals:** Risks include reading fields not valid for shorter SCCB variants, wrong fallback between legacy and extended memory fields, console detection affected by mask compatibility mode, and boot CPU matching assumptions. Test signals include facility bits on LPAR and VM, IPL loadparm preservation, memory size values, line-mode/VT220 detection, and early CPU info parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_early.c -->
