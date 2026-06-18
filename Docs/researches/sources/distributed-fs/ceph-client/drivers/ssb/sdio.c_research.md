<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/sdio.c

Purpose: implements SDIO host-bus access for SSB devices, including SDIO backplane window programming, register/block I/O, CIS tuple invariant extraction, and SDIO bus initialization.

Important APIs/types/functions: `ssb_sdio_ops` supplies SSB bus operations. `ssb_sdio_set_sbaddr_window()` programs SBADDR low/mid/high registers. `ssb_sdio_scan_read32()` and `ssb_sdio_scan_switch_coreidx()` support enumeration. Runtime accessors `ssb_sdio_read8/16/32()`, `ssb_sdio_write8/16/32()`, and optional block read/write helpers claim the SDIO host, switch core, translate offsets, and use SDIO I/O APIs. `ssb_sdio_get_invariants()` parses SDIO tuples into board/SPROM data.

Control flow: enumeration sets the address window to each core base and reads ID registers. Runtime access claims the host, ensures `bus->sdio_sbaddr` matches the target core, combines the lower backplane address with the selected window, sets the 32-bit access flag when needed, performs SDIO I/O, logs errors, and releases the host. A read-after-write quirk can force a dummy read after 32-bit writes.

State and persistence: runtime state is `bus->sdio_sbaddr`, `mapped_device`, parsed SPROM fields, and optional quirk flags. No persistent storage is modified.

Dependencies and integration: depends on MMC/SDIO function APIs, SSB scan and main bus code, tuple data exposed by the SDIO core, and Broadcom SDIO address-window conventions.

Risks: all register access depends on correct host-claiming and address-window cache coherency. Bad tuple sizes fail invariant extraction. Block I/O must preserve alignment expectations for 16/32-bit widths. The 32-bit access flag and read-after-write quirk are hardware-sensitive.

Test signals: enumerate SDIO SSB devices, read/write 8/16/32-bit registers, exercise block transfers, trigger SDIO errors, verify tuple-derived MAC/board fields, and test hardware requiring the read-after-write quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sdio.c -->
