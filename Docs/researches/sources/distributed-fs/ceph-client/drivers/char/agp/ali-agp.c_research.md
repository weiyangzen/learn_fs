# sources/distributed-fs/ceph-client/drivers/char/agp/ali-agp.c

## Purpose
This file implements AGPGART chipset support for ALi host bridges, including special cache-flush behavior for the M1541 chipset.

## Important APIs, Types, and Functions
Important functions include `ali_fetch_size()`, `ali_configure()`, `ali_cleanup()`, `ali_tlbflush()`, `m1541_cache_flush()`, `m1541_alloc_page()`, `ali_destroy_page()`, `m1541_destroy_page()`, `agp_ali_probe()`, and `agp_ali_remove()`. Bridge callback tables are `ali_generic_bridge` and `ali_m1541_bridge`.

## Control Flow
The PCI driver matches ALi host bridges. Probe verifies an AGP capability, matches known ALi device IDs, allocates an AGP bridge, chooses M1541-specific or generic callbacks, reads the AGP status mode, stores bridge data on the PCI device, and calls `agp_add_bridge()`. Configuration writes aperture size/GATT base into `ALI_ATTBASE`, sets TLB control, derives aperture bus address from BAR0, and enables the TLB.

## State and Persistence Behavior
The driver programs ALi PCI config registers for aperture size, GATT base, tag/TLB control, and optional cache flush address. It restores previous aperture size on cleanup. Persistent bridge state is stored in generic `agp_bridge_data`.

## Dependencies and Integration Points
It depends on PCI, AGP backend/generic helpers, ALi PCI IDs, and architecture page/cache helpers. User-facing AGP memory operations flow through generic AGP code into this callback table.

## Risks
The ALi path relies on global `agp_bridge`. The M1541 cache flush sequence writes one flush per GATT page and page allocation/destruction flushes physical addresses; incorrect cache handling can produce stale GART entries. Hidden M1621 ID decoding mutates the displayed chipset name. Cleanup uses previous size but does not fully undo every register bit changed by configure.

## Test Signals
Probe/remove on supported ALi chipsets, validate aperture size detection, GATT base programming, TLB flush on insert/remove, M1541 cache flush behavior, and errata-sensitive graphics cards such as Matrox G200 running in safe modes.
