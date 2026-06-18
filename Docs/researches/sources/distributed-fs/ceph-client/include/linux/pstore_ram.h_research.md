# sources/distributed-fs/ceph-client/include/linux/pstore_ram.h

Purpose: defines platform data for the ramoops persistent RAM pstore backend, including reserved memory layout and ECC configuration.

Important APIs and types: `struct persistent_ram_ecc_info` describes ECC block size, ECC size, symbol size, polynomial, and parity buffer. `RAMOOPS_FLAG_FTRACE_PER_CPU` configures per-CPU ftrace areas. `struct ramoops_platform_data` carries reserved memory size/address/type, record/console/ftrace/pmsg sizes, max dump reason, flags, and ECC info.

Control flow: platform code supplies `ramoops_platform_data` to the ramoops driver; the driver maps reserved RAM, divides it into frontend areas, applies ECC configuration, and registers with pstore.

State and persistence: reserved RAM contents persist across warm reboot if the platform preserves memory. Runtime platform data defines the layout used to interpret that memory.

Dependencies and integration points: depends on pstore core, persistent RAM backend implementation, reserved memory, platform data or equivalent firmware descriptions, and ECC support.

Risks and test signals: risks include reserved memory overlap, size misalignment, ECC parameter mismatch, losing records on memory clearing, and incorrect per-CPU ftrace partitioning. Test boot with reserved memory, panic persistence, ECC correction notices, per-frontend sizing, and reboot record recovery.
