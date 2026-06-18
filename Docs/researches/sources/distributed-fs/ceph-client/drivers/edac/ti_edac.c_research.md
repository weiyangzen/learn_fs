# sources/distributed-fs/ceph-client/drivers/edac/ti_edac.c

Purpose: `ti_edac.c` is an EDAC platform driver for TI EMIF DDR2/DDR3 ECC controllers on Keystone and DRA7xx. It maps EMIF registers, registers one all-memory EDAC layer, decodes memory geometry, and reports interrupt-driven ECC events.

Important APIs/types/functions: `struct ti_edac` holds MMIO. `ti_edac_isr()` reports 1-bit, 2-bit, and write ECC errors and acknowledges status. `ti_edac_setup_dimm()` decodes size/type/width/ECC mode. `_emif_get_id()` orders controllers by OF translated address. `ti_edac_probe()` and `ti_edac_remove()` manage lifecycle.

Control flow: probe matches OF data, maps MMIO, allocates an EDAC MC, fills private data and caps, initializes DIMM metadata, requests IRQ, registers EDAC, programs CE threshold, and enables interrupts. Remove unregisters and frees the MC.

State and persistence: only the MMIO base and EDAC metadata are stored in memory. Hardware counters/logs persist until ISR clears them.

Dependencies/integration: OF compatibles `ti,emif-keystone` and `ti,emif-dra7xx`, platform MMIO/IRQ, EDAC core, and EMIF register definitions.

Risks: K2 memory-type detection may reuse the narrowed-mode value instead of original SDRAM config; `1 << bits` can overflow for large sizes; `_emif_get_id()` assumes valid node addresses; write ECC events have no location.

Test signals: both compatible paths, memory geometry validation, CE/UE/write IRQ injection, counter clearing, threshold programming, and multi-EMIF ID ordering.
