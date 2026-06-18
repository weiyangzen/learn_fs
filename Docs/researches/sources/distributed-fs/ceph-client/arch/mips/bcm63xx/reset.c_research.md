# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/reset.c

Purpose: maps generic BCM63xx reset IDs to CPU-specific soft-reset register bits and exposes reset assertion/deassertion helpers.

Important APIs and functions: macro-generated reset tables define bit positions for SPI, Ethernet, USBH, USBD, DSL, SAR, EPHY, ENETSW, PCM, MPI, PCIe, and PCIe external resets by CPU. `bcm63xx_core_set_reset()` writes the appropriate soft-reset bit with locking and optional delay. `bcm63xx_core_assert()` and `bcm63xx_core_deassert()` are exported wrappers.

Control flow: callers pass a logical reset enum. The helper selects the active CPU reset table, rejects unsupported zero-bit entries, and toggles the soft-reset register.

State and persistence: soft-reset hardware bits are runtime SoC state only. The mutex serializes register updates.

Dependencies and integration points: used by clock and device drivers that must reset BCM63xx peripheral blocks. Depends on CPU detection and PERF soft-reset register definitions.

Risks and test signals: zero-bit unsupported reset entries and CPU-specific mappings are easy to misuse. Test by exercising probe/remove or reset paths for each peripheral, checking register writes, and confirming devices recover after reset toggles.
