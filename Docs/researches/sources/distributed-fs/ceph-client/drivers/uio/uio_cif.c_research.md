# sources/distributed-fs/ceph-client/drivers/uio/uio_cif.c

## Purpose
`uio_cif.c` is a UIO PCI driver for Hilscher CIF Profibus and DeviceNet cards behind a PLX9030 bridge. It exposes BAR0 and BAR2 as physical UIO mappings and supplies an IRQ handler that disables PLX INT1 until userspace handles the device.

## Important APIs, Types, And Functions
The PCI ID table matches PLX9030 devices with Hilscher subvendor and Profibus/DeviceNet subdevices. `hilscher_pci_probe()` enables PCI, requests regions, maps BAR0 internally for interrupt control, publishes BAR0 and BAR2 in `uio_info.mem`, sets a product-specific `info->name`, and registers UIO with shared IRQ handler `hilscher_handler()`. Remove unregisters UIO, releases regions, disables PCI, and unmaps BAR0.

## Control Flow And State
The IRQ handler reads BAR0 `PLX9030_INTCSR`. If INT1 is both enabled and active, it clears `INTSCR_INT1_ENABLE` and returns `IRQ_HANDLED`; otherwise it returns `IRQ_NONE`. UIO core then increments the event counter. Userspace is responsible for device-level acknowledgement and re-enabling.

## Dependencies And Integration Points
The driver depends on PCI, PLX bridge register layout, UIO core, and userspace CIF protocol handling. It integrates through `/dev/uioN` plus `maps/map0` and `maps/map1`.

## Risks And Edge Cases
Only BAR0 is internally mapped, so interrupt control assumes PLX INTCSR is in BAR0. Shared IRQ filtering must be exact. The driver does not provide an `irqcontrol` callback, so re-enable likely requires userspace MMIO writes to BAR0. Probe error paths also return `-ENODEV` for multiple causes.

## Test Signals
Validate both supported subdevices, BAR sysfs map sizes, interrupt disable on INT1, shared IRQ non-ownership returning `IRQ_NONE`, userspace interrupt re-enable, and remove while userspace mappings are active.
