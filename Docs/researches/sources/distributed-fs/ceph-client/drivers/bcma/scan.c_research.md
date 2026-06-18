# sources/distributed-fs/ceph-client/drivers/bcma/scan.c

Purpose: discovers BCMA cores by parsing the hardware enumeration ROM. It detects chip identity, walks EROM component entries, filters bridges/non-core components, records core addresses and wrapper addresses, maps SoC cores, assigns core indexes and unit numbers, and prepares Linux devices for later registration.

Important APIs and functions: `bcma_detect_chip()` switches to the chipcommon base and reads `BCMA_CC_ID`. `bcma_bus_scan()` is the top-level scanner. EROM helpers include `bcma_erom_get_ent()`, `bcma_erom_get_ci()`, `bcma_erom_get_mst_port()`, `bcma_erom_get_addr_desc()`, and `bcma_erom_skip_component()`. `bcma_get_next_core()` parses component info words, port/wrapper counts, slave address descriptors, master/slave wrapper descriptors, applies match filtering, and maps SoC `io_addr`/`io_wrap`.

Control flow: scanning skips if `bus->nr_cores` is already nonzero. It obtains the EROM base from chipcommon; SoC hosts ioremap the EROM while PCI hosts use the mapped BAR window and switch BAR0 to the EROM base. It loops until the EROM end marker, allocating a `bcma_device` per candidate. Return codes from `bcma_get_next_core()` distinguish duplicate index, non-core/bridge, EROM end, invalid sequence, and allocation failure.

State and persistence: the scanner populates `bus->chipinfo`, `bus->nr_cores`, the `bus->cores` list, and each `bcma_device`'s ID, core index, unit, slave addresses, primary address, wrapper address, and SoC MMIO mappings. These objects persist until `bcma_unregister_cores()`.

Dependencies and integration points: depends on scan bit definitions from `scan.h`, BCMA register definitions, Linux MMIO APIs, PCI BAR window switching for PCI-hosted devices, and `bcma_prepare_core()` from `main.c`. Core names are local lookup tables for logging only.

Risks: EROM parsing is strict and returns `-EILSEQ` on unexpected descriptors, which can abort bus registration. The code ignores or skips bridges and ARM dummy components. SoC mapping failures can leak partial assumptions if wrapper mapping fails after core mapping. There is a likely cleanup concern: the final `iounmap(eromptr)` uses the advanced pointer rather than the original mapping. Test signals include scan logs for all expected cores, duplicate-index behavior, bridge skip logs, SoC ioremap/unmap checks, and successful rescans being no-ops.
