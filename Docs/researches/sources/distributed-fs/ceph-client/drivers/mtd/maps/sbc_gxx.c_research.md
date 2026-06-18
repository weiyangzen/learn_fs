# sources/distributed-fs/ceph-client/drivers/mtd/maps/sbc_gxx.c

Purpose: legacy x86 MTD map driver for Arcom SBC-MediaGX/GXm/GX1 boards. It exposes up to 16 MiB of x8 Intel StrataFlash through a 16 KiB memory window and two I/O paging registers, then registers three static partitions for boot, data, and application areas.

Important APIs/types/functions: `sbc_gxx_map`, `sbc_gxx_page()`, `sbc_gxx_read8()`, `sbc_gxx_write8()`, `sbc_gxx_copy_from()`, `sbc_gxx_copy_to()`, `init_sbc_gxx()`, `cleanup_sbc_gxx()`. It depends on low-level port I/O (`outw()`), `ioremap()`, `request_region()`, custom map callbacks, `do_map_probe("cfi_probe")`, and `mtd_device_register()`.

Control flow: init maps the fixed memory aperture, reserves paging ports, logs address ranges, probes CFI over custom map operations, and registers static partitions. Each map access takes `sbc_gxx_spin`, pages the target flash address into the 16 KiB window if needed, then performs byte or bulk I/O. Cleanup unregisters and destroys the MTD, unmaps the aperture, and releases I/O ports.

State and persistence: persistent state is board flash. Runtime state is global: `page_in_window`, `iomapadr`, `all_mtd`, and spinlock. The page cache avoids repeated port writes but has no hardware validation.

Risks and test signals: access serialization is critical because reads/writes change a global hardware page register. Bulk copy paths must handle window-boundary splitting exactly. Probe failure cleanup should release both mappings and I/O ports. Tests should cover reads/writes across 16 KiB boundaries, partition sizes, failed `ioremap()`, failed `request_region()`, and absent CFI flash.
