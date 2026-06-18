# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pasemi_nand.c

Purpose: this driver supports the PA Semi PWRficient on-chip localbus NAND interface. It exposes a single raw NAND chip through legacy command, buffer, and ready callbacks, with the LPC control/status register discovered through a PA Semi PCI device.

Important APIs, types, and functions: `struct pasemi_ddata` stores the `nand_chip`, controller, and LPC control port address. `pasemi_hwcontrol()` sends CLE/ALE cycles using fixed localbus pin offsets and flushes posted writes through `eieio()` plus an LPC control read. `pasemi_device_ready()` checks `LBICTRL_LPCCTL_NR`. `pasemi_read_buf()` and `pasemi_write_buf()` transfer in 0x800-byte chunks with `memcpy_fromio()`/`memcpy_toio()`. `pasemi_attach_chip()` defaults software ECC to Hamming.

Control flow: probe resolves the OF resource, allocates private state, maps the NAND window, locates PCI vendor/device `PCI_VENDOR_ID_PASEMI, 0xa008`, reserves four LPC control IO bytes, installs legacy NAND callbacks, enables flash BBT storage, defaults the ECC engine to software, scans one chip, and registers the MTD device. Failure paths release the IO region, unmap MMIO, and free the state. Remove unregisters MTD, cleans NAND, releases the LPC region, unmaps MMIO, and frees memory.

State and persistence: persistent driver state is the mapped data window, LPC control port, NAND core state, and flash-based bad block table option. There is no PM implementation; hardware state is expected to be valid while bound.

Dependencies and integration points: this file depends on OF address mapping, PCI discovery for the localbus controller, raw NAND legacy callbacks, MTD registration, PA Semi-specific IO ordering, and the compatible `pasemi,localbus-nand`.

Risks: the driver hard-codes CLE/ALE pin offsets and the PCI device ID used to find the ready/control register, so it is tightly coupled to the original platform. It uses non-devm allocation and manual cleanup, making probe error paths important. The same IO address is assigned to read and write; incorrect resource mapping is catastrophic. Flash BBT changes on-media state and should be compatible with existing boot firmware expectations.

Test signals: successful OF resource mapping, PCI LPC controller discovery, request-region conflict handling, NAND ID/read/write cycles, ready polling via `LBICTRL_LPCCTL_NR`, Hamming software ECC default, flash BBT creation/reuse, and remove-path resource release.
