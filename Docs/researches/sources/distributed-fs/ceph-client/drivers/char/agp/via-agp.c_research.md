# sources/distributed-fs/ceph-client/drivers/char/agp/via-agp.c

## Purpose

`via-agp.c` is the AGPGART driver for VIA host bridges. It supports legacy AGP register layouts and an AGP3 register layout selected by `VIA_AGPSEL`, while using generic GATT allocation and memory insertion/removal.

## Important APIs, Types, And Functions

- Legacy hooks: `via_fetch_size()`, `via_configure()`, `via_cleanup()`, and `via_tlbflush()`.
- AGP3 hooks: `via_fetch_size_agp3()`, `via_configure_agp3()`, `via_cleanup_agp3()`, and `via_tlbflush_agp3()`.
- Driver descriptors: `via_driver` and `via_agp3_driver`.
- Device mapping: `via_agp_device_ids[]` and ordered `agp_via_pci_table[]`.
- Probe helpers: `check_via_agp3()`, `agp_via_probe()`, `agp_via_remove()`, and `agp_via_resume()`.

## Control Flow

Module init registers a PCI host-bridge driver. Probe uses the PCI ID table index to print a chipset name, allocates a bridge with the legacy driver, applies a KT400-disguised-as-KT266 check, reads AGP version, and calls `check_via_agp3()` for AGP3-capable bridges. Legacy configure writes APSIZE, records aperture bus base, enables GART control, and writes ATTBASE with low enable bits. AGP3 configure writes the AGP3 ATTBASE and enables GTLB/aperture bits in `VIA_AGP3_GARTCTRL`. Resume reruns the configure method matching the selected driver.

## State And Persistence Behavior

Persistent bridge state is standard `agp_bridge_data`; chipset state is in VIA PCI config registers. GATT allocation and entry state are handled by generic AGP helpers. Driver selection is per bridge pointer, unlike the mutable-global pattern used by SiS.

## Dependencies And Integration Points

The file depends on `agp.h`, PCI IDs, and generic AGP3 size tables/helpers for memory management and mode enable. It integrates with the AGP core via `agp_bridge_driver` callbacks and uses `agp_device_ids` for readable chipset names.

## Risks And Edge Cases

`via_agp3_driver` declares `size_type = U8_APER_SIZE` while its `aperture_sizes` points to `agp3_generic_sizes` and `via_fetch_size_agp3()` treats entries as `aper_size_info_16`; generic GATT creation uses `size_type`, so this mismatch is a notable correctness risk unless avoided by runtime path assumptions. `via_cleanup_agp3()` writes to `VIA_APSIZE` instead of `VIA_AGP3_APSIZE`, which may be intentional compatibility or a register bug. The name table and PCI table must remain in identical order. The KT400 disguise workaround depends on subsystem ID.

## Test Signals

Compile with VIA AGP enabled, probe legacy and AGP3 VIA hardware, verify name-table alignment, confirm AGP3 driver selection through `VIA_AGPSEL`, and run allocation/bind/unbind tests across the selected aperture size. Static tests should inspect the AGP3 `size_type` mismatch and cleanup register choice.
