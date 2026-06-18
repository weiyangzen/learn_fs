# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nforce2.c

Purpose: PCI SMBus driver for NVIDIA nForce2/3/4/5xx chipsets. It exposes one or two SMBus adapters using I/O-port register access and supports common SMBus protocol operations, optional block operations, PEC bits, and abort on selected chipsets.

Important APIs/types: `struct nforce2_smbus` contains adapter, I/O base, region size, block-operation support, and abort capability. Main functions are `nforce2_access()`, `nforce2_check_status()`, `nforce2_abort()`, `nforce2_probe_smb()`, `nforce2_probe()`, and `nforce2_remove()`. `smbus_algorithm` provides `.smbus_xfer` and `.functionality`.

Control flow: PCI probe allocates two bus structs, enables block/abort flags for selected device IDs, probes SMBus 1 from BAR4 or legacy config register `0x50`, probes SMBus 2 from BAR5 or `0x54` unless DMI-blacklisted, requests I/O regions, and registers adapters. SMBus access writes command/data/count registers according to requested protocol, writes the target address and protocol register to start, polls status up to 100 ms, optionally aborts on timeout, and reads back byte/word/block data for reads.

State and persistence: adapter state persists per PCI device until remove. There is no interrupt or PM state. I/O regions are reserved while adapters exist. The DMI blacklist disables the second bus for a known unsafe board.

Dependencies and integration: depends on PCI IDs for nForce SMBus devices, ACPI region conflict checking, DMI matching, I/O port accessors, Linux SMBus core, and resource reservation. It registers hardware-monitor class adapters.

Risks: the driver assumes at most one nForce device with two interfaces. Polling status treats any status bits besides DONE as failure without deeper decoding. Block write loops all 32 bytes regardless of requested length after programming the length. Older nonstandard BAR fallback relies on raw PCI config words. The abort mechanism exists only on selected devices and may fail to reset the bus.

Test signals: cover BAR and legacy-base discovery, ACPI region conflicts, DMI second-bus blacklist, quick/byte/byte-data/word/block read and write, PEC protocol bit setting, block length validation, timeout with and without abort support, partial adapter registration where only one bus succeeds, and remove resource release.
