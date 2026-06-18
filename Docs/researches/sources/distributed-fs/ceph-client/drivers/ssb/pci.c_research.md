# sources/distributed-fs/ceph-client/drivers/ssb/pci.c

## Purpose
PCI-host backend for SSB: manages BAR0 core window switching, PCI xtal/PLL control, SPROM reading/writing/parsing, board invariant extraction, PCI MMIO access ops, and a sysfs SPROM attribute.

## Important APIs, Types, and Functions
Public functions include `ssb_pci_switch_coreidx`, `ssb_pci_switch_core`, `ssb_pci_xtal`, `ssb_pci_get_invariants`, `ssb_pci_init`, `ssb_pci_exit`, and `ssb_pci_ops`. SPROM helpers include CRC calculation/checking, read/write, revision-specific extraction (`sprom_extract_r123`, `r45`, `r8`), fallback handling, and sysfs show/store callbacks.

## Control Flow
Core switching writes `SSB_BAR0_WIN`, reads it back until the requested core index is mapped, and updates `bus->mapped_device` under `bar_lock`. `ssb_pci_xtal` toggles PCI GPIO output/enable bits for XTAL/PLL and clears target-abort status on power-up. SPROM get selects offset based on ChipCommon revision/status, tries legacy and rev4+ sizes with CRC, falls back to platform SPROM when both fail, then extracts fields by revision. MMIO ops assert the bus is powered, switch core if needed, then perform ioread/iowrite or block I/O. Init creates an admin RW `ssb_sprom` file on the host PCI device.

## State and Persistence
State includes `bus->mapped_device`, `sprom_mutex`, `sprom_offset`, `sprom_size`, parsed `bus->sprom`, board info, power warning count, and hardware PCI GPIO/BAR/window/SPROM contents. `sprom_do_write` persistently writes SPROM and must not be interrupted.

## Dependencies and Integration Points
Used by SSB main registration for PCI buses, SPROM invariants, and `ssb_pci_ops`. Depends on Linux PCI config access, MMIO, SPROM fallback infrastructure, sysfs device attributes, and `ssb_pci_dev_to_bus`.

## Risks
BAR window switching failures break all core access. MMIO while powered down logs fatal errors and returns all-ones values, so callers may misinterpret absent hardware. SPROM write is slow and persistent; bad CRC validation or interrupted power can brick calibration data. Unsupported SPROM revisions fall back to v1 extraction, risking incomplete wireless calibration.

## Test Signals
Validate core switching under concurrent access, xtal/PLL power transitions, SPROM sysfs read/write CRC enforcement, fallback SPROM path, parsed board/mac/power fields for revisions 1/2/3/4/5/8, and powered-down access warnings.
