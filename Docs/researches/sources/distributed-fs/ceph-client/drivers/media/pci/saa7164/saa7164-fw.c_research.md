<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-fw.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-fw.c

Purpose: firmware loader for SAA7164 bridge revisions. It detects existing ROM/loaded firmware, validates revision-specific firmware file size and headers, optionally updates a second-stage bootloader, downloads images through MMIO mailboxes, and marks firmware loaded.

Important APIs, types, and functions: `saa7164_downloadfirmware()` is the external entry point. `saa7164_downloadimage()` copies firmware chunks into device download memory and performs download/data-ready handshakes. `saa7164_dl_wait_ack()` and `saa7164_dl_wait_clr()` poll flag registers. `struct fw_header` describes firmware image metadata.

Control flow: the loader checks current firmware version and bootloader status flags. If firmware is absent, it requests `v4l-saa7164-1.0.2-3.fw` for rev2 or `NXP7164-2010-03-10.1.fw` for rev3, validates exact size, parses bootloader/firmware sections, then downloads either bootloader plus firmware or firmware only. Completion waits for boot flags and final version.

State and persistence: reads firmware files through kernel firmware API but does not write storage. Device state changes are MMIO download flags, ready flags, deadlock register, and `dev->firmwareloaded`.

Dependencies and integration points: Linux firmware loader, SAA7164 register definitions, core firmware-status helpers, board chip revision metadata, and BAR0 MMIO.

Risks: several timeout counters subtract 10 but sleep 100 ms, making nominal timeouts misleading. Firmware size is exact-match, so alternate packaged firmware variants fail. A comment notes a possible bounds overrun with old firmware. Download uses a fixed 4 MiB staging buffer and assumes firmware section metadata is trustworthy after size validation.

Test signals: cold boot with no firmware, warm boot with firmware already present, rev2/rev3 file selection, missing or wrong-size firmware errors, bootloader update/no-update paths, deadlock detection, and successful post-load command bus communication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-fw.c -->
