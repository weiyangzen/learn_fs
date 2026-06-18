# sources/distributed-fs/ceph-client/drivers/mtd/devices/spear_smi.c

Purpose: ST SPEAr Serial Memory Interface controller driver for attached serial NOR flashes. It replaces the normal SPI controller path with SMI hardware modes and registers one MTD per detected bank.

Important APIs/types/functions: `struct spear_smi` owns clock, registers, IRQ wait queue, controller lock, and bank pointers. `struct spear_snor_flash` owns per-bank MTD, lock, geometry, base memory window, erase command, and fast-mode flag. Key helpers are `spear_smi_read_sr()`, `spear_smi_wait_till_ready()`, `spear_smi_int_handler()`, `spear_smi_hw_init()`, `spear_smi_write_enable()`, `spear_smi_erase_sector()`, `spear_smi_probe_flash()`, and `spear_smi_setup_banks()`. MTD callbacks are `spear_mtd_read()`, `spear_mtd_write()`, and `spear_mtd_erase()`.

Control flow: platform probe obtains DT/platform data, IRQ, MMIO, clock, initializes hardware and wait queue, then probes each configured bank via RDID in software mode. A matched flash gets its memory window ioremapped, MTD geometry filled from the device table, and registered. Reads switch to hardware read mode and `memcpy_fromio()` from the bank window. Writes wait ready, issue write-enable, enable write-burst mode, then copy bytes/words to I/O memory respecting hardware write-size constraints. Erase loops sector commands.

State and persistence: flash contents are persistent NOR data. Runtime state includes controller register mode, last IRQ status, wait queue completions, per-bank locks, and MTD registrations. No filesystem or wear metadata is stored by the driver.

Dependencies/integration: platform bus, optional OF compatible `st,spear600-smi`, `linux/mtd/spear_smi.h` platform data, clocks, IRQs, I/O memory, MTD partitions, and NOR flash ID table.

Risks: DT parsing allocates one `board_flash_info` but iterates children as if multiple entries exist, which is a potential array/logic hazard. Many operations depend on interrupts and status bits with short timeouts. Write-burst mode requires uniform incremental access; the driver uses byte copies for unaligned cases to avoid mixed access sizes.

Test signals: probe with multiple banks, RDID failure, IRQ timeout paths, fast-mode reads, page-boundary writes, unaligned write-buffer paths, sector erase loops, suspend/resume clock reinitialization, and unregistering all banks.
