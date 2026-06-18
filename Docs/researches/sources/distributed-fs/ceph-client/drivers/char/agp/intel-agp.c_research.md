# sources/distributed-fs/ceph-client/drivers/char/agp/intel-agp.c

## Purpose

`intel-agp.c` is the legacy Intel AGPGART PCI host-bridge driver. It supports pre-GEM Intel AGP chipsets and selects either a true AGP bridge driver or, for integrated GMCH graphics handled by `intel-gtt.c`, a fake AGP/GTT path.

## Important APIs, Types, And Functions

- Aperture size readers: `intel_fetch_size()`, `intel_8xx_fetch_size()`, and `intel_815_fetch_size()` parse Intel APSIZE variants.
- TLB and cleanup hooks: `intel_tlbflush()`, `intel_8xx_tlbflush()`, `intel_820_tlbflush()`, `intel_cleanup()`, `intel_8xx_cleanup()`, and `intel_820_cleanup()`.
- Chipset configuration hooks: `intel_configure()`, `intel_815_configure()`, `intel_820_configure()`, `intel_840_configure()`, `intel_845_configure()`, `intel_850_configure()`, `intel_860_configure()`, `intel_830mp_configure()`, and `intel_7505_configure()`.
- Static tables: Intel aperture-size arrays, `intel_generic_masks`, multiple `agp_bridge_driver` instances, and `intel_agp_chipsets[]`.
- PCI integration: `agp_intel_probe()`, `agp_intel_remove()`, `agp_intel_resume()`, `agp_intel_pci_table[]`, and `agp_intel_pci_driver`.

## Control Flow

The module registers `agpgart-intel` unless `agp_off` is set. Probe allocates a bridge, records the AGP capability offset, first calls `intel_gmch_probe()` to allow integrated graphics GTT ownership, then falls back to matching legacy host bridge IDs in `intel_agp_chipsets[]`. For real AGP paths it may assign BAR0 if firmware left the aperture unassigned, enables the PCI device, reads the mode register, stores bridge drvdata, and calls `agp_add_bridge()`. Configure hooks program APSIZE, aperture bus base, ATTBASE/GATT pointer, AGPCTRL, chipset enable bits, and error status registers. Resume simply reruns `bridge->driver->configure()`.

## State And Persistence Behavior

State is mostly stored in `agp_bridge_data`: selected driver, capability offset, current/previous aperture sizes, `gart_bus_addr`, `gatt_bus_addr`, mode, and optional `apbase_config` preservation for i845-style reconfiguration. Hardware state persists in Intel PCI config registers until cleanup or resume reprogramming. The driver relies on `generic.c` for GATT memory state and page accounting.

## Dependencies And Integration Points

The file depends on `agp.h`, `intel-agp.h`, generic AGP helpers, PCI IDs, and `<drm/intel/intel-gtt.h>`. Its main integration point is `intel_gmch_probe()`/`intel_gmch_remove()` in `intel-gtt.c`, which intercept integrated-GPU host bridges. It registers with the kernel PCI core and exports no direct APIs of its own.

## Risks And Edge Cases

The i815 path rejects GATT bus addresses that exceed reserved ATTBASE bits. Firmware may omit aperture BAR assignment, so probe contains early resource repair before `pci_enable_device()`. Several chipsets have unique enable and error registers, making table-to-driver selection high risk. GMCH probing can change the bridge driver path entirely; ordering with DRM/i915 and refcounted GTT ownership matters. Resume assumes `bridge->driver` is valid and reconfiguration is sufficient after power management.

## Test Signals

Compile with `CONFIG_AGP_INTEL`; verify `agpgart-intel` probes expected PCI IDs and logs the selected chipset. Hardware tests should check aperture BAR assignment, APSIZE restoration on cleanup, GATT ATTBASE programming, suspend/resume reconfiguration, and no regression in the integrated GMCH fake-AGP path. Static review should compare `agp_intel_pci_table[]` against `intel_agp_chipsets[]` and `intel_gtt_chipsets[]` for intentional coverage gaps.
