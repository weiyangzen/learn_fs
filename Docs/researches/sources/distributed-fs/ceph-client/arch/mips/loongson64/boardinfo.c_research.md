<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c

Purpose: Exposes Loongson64 board and BIOS information under firmware sysfs.

Important APIs/types/functions: `boardinfo_show()` formats data from `eboard`, `einter`, and `especial`; `boardinfo_init()` creates `/sys/firmware/lefi/boardinfo`.

Control flow: Late init creates a `lefi` kobject under `firmware_kobj` and adds a read-only `boardinfo` attribute.

State and persistence: Sysfs kobject and attribute persist until shutdown. It reads firmware table globals initialized by `env.c`.

Dependencies and integration: Requires LEFI-style boot parameter structures in `boot_param.h` and `CONFIG_SYSFS`.

Risks: Assumes firmware pointers are valid and strings contain dash-separated vendor/manufacturer parts. No cleanup path is needed for late init but partial creation failure only returns an error.

Test signals: `/sys/firmware/lefi/boardinfo` should show board manufacturer/name, BIOS vendor/version, and release date on LEFI systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c -->
