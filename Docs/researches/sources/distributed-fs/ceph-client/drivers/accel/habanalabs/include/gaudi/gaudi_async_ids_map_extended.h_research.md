## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_ids_map_extended.h

### Purpose
`gaudi_async_ids_map_extended.h` is the generated lookup table that maps Gaudi firmware-controller event IDs to CPU interrupt/event IDs and textual names. It is the concrete decode table used with `gaudi_async_events.h`.

### Important APIs, Types, And Functions
The file defines `struct gaudi_async_events_ids_map` with `fc_id`, `cpu_id`, `valid`, and a fixed `name[64]`, then defines static `gaudi_irq_map_table[]`. The table has 663 entries for `fc_id` 0 through 662; 312 entries are valid and 351 are explicit invalid gaps. Early entries map PCIe/TPC/MME/DMA/SRAM/HBM errors, midrange entries map decoder/PLL/SEI/BMON/SPMU/MMU events, and the final entries map QMAN, DMA core, NIC QP, PI/update/control, firmware alive, reset, status, and fixed power/thermal environment events.

### Control Flow
There is no function body in the header. During initialization, `gaudi.c` iterates `ARRAY_SIZE(gaudi_irq_map_table)` and copies valid `fc_id` values into the device event array, bounded by `GAUDI_EVENT_SIZE`. Runtime event handling indexes by event type, checks `.valid`, uses `.cpu_id` for interrupt routing, and uses `.name` for user-visible descriptions.

### State, Persistence, And Dependencies
The table is static driver data compiled into the kernel module. It persists for module lifetime and is read-only by convention even though it is not declared `const`. It depends on numeric event IDs from firmware and on the enum ranges in `gaudi_async_events.h` staying in sync with the table indices.

### Integration Points
`gaudi.c` uses the table for event registration, CPU event routing, description lookup, QMAN interrupt enablement, DMA/NIC/TPC/MME event diagnostics, and command/control events such as `PI_UPDATE`, `HALT_MACHINE`, and `DEV_RESET_REQ`. Userspace-visible event statistics are indexed by the enum and effectively depend on this table.

### Risks
The table is positional and sparse. If a new valid event is added without updating the enum or if a gap is collapsed, event IDs will be decoded incorrectly. The non-`const` static definition in a header also means each translation unit including it would get a private table; this is safe only while inclusion remains limited and intentional. Name truncation would affect diagnostics if future names exceed 63 bytes.

### Test Signals
Check that table length is at least `GAUDI_EVENT_SIZE`, all enum-defined valid events have matching table rows, invalid rows are rejected, and event-name lookup returns expected strings. Firmware-driven or synthetic event tests should verify routing for TPC, MME, DMA, NIC, MMU, PLL, and control events, including gaps around sparse ranges.
