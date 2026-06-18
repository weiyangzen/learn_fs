# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770_osm.c

## Purpose
`aic7770_osm.c` is the Linux OS-specific EISA attachment glue for AIC7770-based aic7xxx controllers. It maps I/O regions and IRQs, binds EISA IDs to the generic `aic7770_config()` path, registers the resulting SCSI host, and tears resources down on removal.

## Important APIs, Types, And Functions
The core exported glue functions are `aic7770_map_registers()` and `aic7770_map_int()`. EISA bus callbacks are `aic7770_probe()` and `aic7770_remove()`. Module-level EISA registration helpers are `ahc_linux_eisa_init()` and `ahc_linux_eisa_exit()`. `aic7770_ids` maps EISA IDs to offsets in `aic7770_ident_table`.

## Control Flow
`aic7770_probe()` computes the slot I/O base, creates an `ahc_eisa` name, allocates an `ahc_softc`, stores the Linux device pointer, calls `aic7770_config()`, stores the softc in driver data, and registers the SCSI host. `aic7770_map_registers()` requests the I/O region and records PIO bus-space fields. `aic7770_map_int()` chooses shared IRQ mode unless the core marked the interrupt edge-triggered, then requests `ahc_linux_isr`. Removal unregisters the SCSI host, disables interrupts under lock, and frees the softc.

## State And Persistence Behavior
Persistent runtime state is in `struct ahc_softc` and platform data: requested I/O port, IRQ number, Linux device pointer, registered SCSI host, and driver data pointer. No disk persistence exists. Resource ownership is transferred to the softc cleanup path after successful config.

## Dependencies And Integration Points
The file depends on Linux device/EISA APIs, resource APIs, IRQ APIs, and aic7xxx Linux OSM helpers from `aic7xxx_osm.h`. It is conditionally included in the `aic7xxx` build by the Makefile when `CONFIG_EISA` is enabled.

## Risks
If `ahc_alloc()` fails after `kstrdup()` succeeds, the allocated name is not explicitly freed in this file. After `aic7770_config()` succeeds but `ahc_linux_register_host()` fails, cleanup responsibility depends on the returned error path. IRQ sharing depends on the core correctly setting `AHC_EDGE_INTERRUPT`.

## Test Signals
Signals include EISA ID table matching, successful I/O region request, correct shared versus edge IRQ flags, `aic7770_config()` success, `ahc_linux_register_host()` success, SCSI host removal on device removal, interrupt disable before free, and unregister behavior on module unload.
