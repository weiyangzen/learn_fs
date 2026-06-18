# sources/distributed-fs/ceph-client/drivers/char/agp/sis-agp.c

## Purpose

`sis-agp.c` is the AGPGART PCI driver for SiS host bridges. It supports older SiS AGP setup and can switch to generic AGP 3.x routines for bridges that advertise sufficiently new AGP versions or when forced by module parameter.

## Important APIs, Types, And Functions

- Module parameters: `agp_sis_force_delay` enables a delayed-enable workaround, and `agp_sis_agp_spec` forces SiS-specific or generic AGP3 setup.
- Core hooks: `sis_fetch_size()`, `sis_configure()`, `sis_cleanup()`, `sis_tlbflush()`, and `sis_delayed_enable()`.
- `sis_get_driver()` mutates `sis_driver` based on chipset workarounds and AGP version.
- PCI integration: `agp_sis_probe()`, `agp_sis_remove()`, `agp_sis_resume()`, PCI ID table, and `agp_sis_pci_driver`.

## Control Flow

Probe validates the AGP capability, allocates a bridge using `sis_driver`, reads AGP version/mode, calls `sis_get_driver()` to apply delay or AGP3 behavior, and registers the bridge. The SiS configure path programs TLB control, records aperture bus base, writes ATTBASE, and sets APSIZE. The delayed-enable path writes AGP commands to each AGP device and sleeps after programming the bridge on broken chipsets to avoid a transient rate-change failure.

## State And Persistence Behavior

The selected driver state is global because `sis_driver` is a mutable static structure. Hardware state persists in SiS PCI config registers `SIS_TLBCNTRL`, `SIS_ATTBASE`, `SIS_APSIZE`, and `SIS_TLBFLUSH`. Bridge state and GATT pages are managed by generic AGP helpers.

## Dependencies And Integration Points

The driver depends on Linux PCI IDs, AGP backend helpers, generic AGP3 helpers, and module parameters. It integrates with the AGP core through `agp_bridge_driver` callbacks and uses generic GATT insertion/removal.

## Risks And Edge Cases

Mutating the global `sis_driver` during probe can affect later devices if multiple SiS bridges existed. The AGP3 switch changes `size_type` to `U16_APER_SIZE`, but the `via`-style mismatch risk is avoided here because it points at `agp3_generic_fetch_size()`. Delay workaround selection depends on a short broken-chipset list unless forced. Resume calls the current global driver's configure method, so per-device configuration could be wrong after global mutation.

## Test Signals

Compile and probe supported SiS IDs, verify `agp_sis_agp_spec` modes select the intended callbacks, check delayed-enable logs and 10 ms bridge delay on 648/746 or forced mode, and validate bind/unbind through generic GATT routines. Static review should flag global driver mutation if multi-device support is relevant.
