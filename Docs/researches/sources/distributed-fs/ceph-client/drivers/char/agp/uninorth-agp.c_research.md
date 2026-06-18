# sources/distributed-fs/ceph-client/drivers/char/agp/uninorth-agp.c

## Purpose

`uninorth-agp.c` implements Apple UniNorth and U3 AGPGART support for PowerPC systems. It handles Apple-specific GART registers, GATT allocation with non-cacheable mappings, revision-specific AGP command errata, optional platform power-management hooks, and module-parameter aperture sizing.

## Important APIs, Types, And Functions

- Global controls: `uninorth_rev`, `is_u3`, `scratch_value`, and module parameter `aperture`.
- Core hooks: `uninorth_fetch_size()`, `uninorth_configure()`, `uninorth_cleanup()`, `uninorth_tlbflush()`, `uninorth_insert_memory()`, `uninorth_remove_memory()`, and `uninorth_agp_enable()`.
- PM hooks under `CONFIG_PM`: `agp_uninorth_suspend()` and `agp_uninorth_resume()`.
- GATT lifecycle: `uninorth_create_gatt_table()`, `uninorth_free_gatt_table()`, `null_cache_flush()`, and `uninorth_priv.pages_arr`.
- Driver descriptors: `uninorth_agp_driver`, `u3_agp_driver`, `uninorth_agp_device_ids[]`.
- PCI integration: `agp_uninorth_probe()`, `agp_uninorth_remove()`, table and module init/exit.

## Control Flow

Probe matches Apple host bridges, locates AGP capability, identifies known UniNorth/U3 IDs, reads Open Firmware `device-rev` from `uni-n` or `u3`, registers platform AGP PM callbacks, allocates an AGP bridge, chooses U3 or UniNorth driver, sets fast-write errata, reads mode, and registers the bridge. GATT creation selects aperture size from the module parameter or default, allocates contiguous pages, marks pages reserved, creates a non-cacheable `vmap`, computes a chipset-specific scratch entry, and fills all GATT slots. Configure writes GART base/size, forces `gart_bus_addr` to zero for a hardware quirk, writes AGP base, and sets U3 dummy page if needed.

## State And Persistence Behavior

State includes GATT pages, the non-cacheable mapping, scratch value, revision flags, and bridge private data used during suspend/resume to save AGP command state. Hardware state persists in UniNorth/U3 GART and AGP command registers until cleanup or PM transitions. The driver marks `cant_use_aperture`, reflecting architecture/hardware access constraints.

## Dependencies And Integration Points

Dependencies include PowerPC Open Firmware APIs, `asm/uninorth.h`, `pmac_feature` AGP PM registration, `vmap`, cache flush primitives, and generic AGP helpers. It integrates with AGP core bridge registration and with video-driver-driven PM callbacks rather than standard PCI PM.

## Risks And Edge Cases

The driver intentionally sets `gart_bus_addr` to zero due to a UniNorth aperture bug, which is surprising to generic callers. U3 and older UniNorth scratch entry formats differ. Revision-specific errata disable AGP 4x or cap request depth. GATT allocation failure must unreserve/free pages and `pages_arr`; error path currently frees pages without clearing `PageReserved` if failure happens after marking but before `vmap` success. PM callbacks assume only one suspend is active via `dev_private_data`.

## Test Signals

On supported Apple PowerPC hardware, verify aperture module parameter parsing, GATT non-cacheable mapping creation, AGP enable command retry success, revision-specific logs/behavior, and suspend/resume through registered PM callbacks. Bind/unbind should show scratch-value occupancy checks and no stale GATT entries. Static review should cover GATT allocation cleanup after partial reservation.
