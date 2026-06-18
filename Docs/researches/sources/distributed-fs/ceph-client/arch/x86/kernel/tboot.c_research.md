# sources/distributed-fs/ceph-client/arch/x86/kernel/tboot.c

## Purpose
`tboot.c` provides Intel TXT/tboot measured-launch runtime support: shared-page discovery, executable identity mappings for tboot shutdown, ACPI sleep routing, AP wait-for-SIPI coordination, debugfs log exposure, and DMA-protected DMAR table retrieval.

## Important APIs, Types, And Functions
Key functions are `tboot_enabled()`, `tboot_probe()`, `tboot_shutdown()`, `tboot_get_dmar_table()`, and `tboot_late_init()`. Internals include `check_tboot_version()`, `map_tboot_page(s)()`, `tboot_create_trampoline()`, `tboot_setup_sleep()`, `tboot_sleep()`, `tboot_extended_sleep()`, `tboot_dying_cpu()`, and `tboot_log_read()`.

## Control Flow
Probe validates `boot_params.tboot_addr` against reserved E820 memory, fixmaps the shared page, and checks UUID/version. Late init maps tboot pages executable at identity addresses, registers CPUHP dying callbacks, debugfs, and ACPI sleep hooks. Shutdown fills ACPI/MAC state for S3 when needed, writes shutdown type, switches CR3 to the tboot page directory, jumps to `shutdown_entry`, and halts if it returns.

## State, Persistence, Dependencies, Integration
Persistent state includes the `tboot` pointer, shared page, `tboot_pg_dir`, `tboot_mm`, AP counters, debugfs file, ACPI callbacks, and retained TXT heap mapping for DMAR. Dependencies include boot params, E820, fixmap/ioremap, page-table allocation, ACPI FADT/FACS, real-mode wakeup, CPU hotplug, debugfs, and TXT config registers. SMP and ACPI code call into it during shutdown/sleep.

## Risks And Test Signals
CR3 switching and executable identity mappings are high-risk. MAC regions, TXT heap walking, and fixed physical debug log mapping are layout-sensitive. Test tboot present/absent, invalid UUID/version/E820, S3/S4/S5, reduced-hardware sleep rejection, CPU wait-for-SIPI counts, debugfs log validation, and DMAR table replacement.
