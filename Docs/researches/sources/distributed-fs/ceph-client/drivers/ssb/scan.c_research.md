<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/scan.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/scan.c

Purpose: discovers SSB cores on native, PCI, PCMCIA, and SDIO host buses and initializes the bus chip identity and per-core `struct ssb_device` table.

Important APIs/types/functions: `ssb_core_name()` maps core IDs to readable names. `ssb_bus_scan()` is the main scanner. `scan_read32()` and `scan_switchcore()` abstract host-bus-specific reads and core switching. `ssb_ioremap()` and `ssb_iounmap()` map/unmap host address space. Fallback helpers `pcidev_to_chipid()` and `chipid_to_nrcores()` handle older chips without usable ChipCommon core count.

Control flow: scan maps host I/O, switches to core 0, reads `SSB_IDHIGH`, detects ChipCommon when present, populates chip ID/revision/package/capabilities, computes core count, remaps full native SSB space when needed, then iterates every core. It fills each `struct ssb_device`, records special core pointers for ChipCommon, EXTIF, MIPS, and PCI/PCIe, filters unsupported duplicate 802.11 cores, ignores dangling Ethernet cores on wireless PCI devices, and adjusts `bus->nr_devices`.

State and persistence: runtime bus state includes `mmio`, chip metadata, `nr_devices`, `devices[]`, and subsystem core pointers. No durable state is written.

Dependencies and integration: calls PCI, PCMCIA, and SDIO switching helpers and uses SSB register definitions. Later SSB driver registration and core initialization consume the populated device table.

Risks: fallback chip/core tables must cover legacy IDs or scanning degrades to one core. Duplicate-core filtering is policy-sensitive and can hide functional cores. Host-specific reads use different address math, so segment/window bugs can corrupt enumeration.

Test signals: scan PCI, PCMCIA, SDIO, and native SSB hosts; verify chip metadata, core count, duplicate 802.11 handling, PCI-vs-PCIe core filtering, and clean unmap on mid-scan errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/scan.c -->
