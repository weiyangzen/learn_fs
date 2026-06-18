# sources/distributed-fs/ceph-client/drivers/uio/uio_mf624.c

## Purpose
`uio_mf624.c` is a UIO PCI driver for the Humusoft MF624 data-acquisition card. It exposes the card's control/status, ADC/DAC/DIO, and counter/timer BARs to userspace and provides interrupt filtering plus userspace IRQ enable/disable control.

## Important APIs, Types, And Functions
The PCI ID table matches Humusoft MF624. `mf624_pci_probe()` enables PCI, requests regions, fills `uio_info`, maps BAR0/BAR2/BAR4 with `mf624_setup_mem()`, installs shared IRQ handler `mf624_irq_handler()`, installs `mf624_irqcontrol()`, registers UIO, and stores drvdata. `mf624_disable_interrupt()` and `mf624_enable_interrupt()` manipulate ADC, CTR4, and global PCI interrupt enable bits in BAR0 `INTCSR`.

## Control Flow And State
The IRQ handler reads `INTCSR`. If ADC interrupt is enabled and pending, it disables ADC/global interrupt and returns `IRQ_HANDLED`; if counter 4 is enabled and pending, it disables CTR4/global interrupt and returns handled; otherwise it returns `IRQ_NONE`. Userspace receives a UIO event, acknowledges hardware through mapped registers, then writes `1` to `/dev/uioN` to re-enable all supported interrupt sources or `0` to disable all. Remove disables all interrupts, unregisters UIO, releases PCI resources, disables the device, and unmaps all three BARs.

## Dependencies And Integration Points
The driver depends on PCI, UIO core, and device-specific BAR/register layout. Userspace is responsible for DAQ operation, interrupt acknowledgement, and source-specific policy using the mapped BARs.

## Risks And Edge Cases
The code trusts BAR0/BAR2/BAR4 despite a note that the datasheet's BAR description is unreliable. IRQ control only recognizes values 0 and 1 but returns success for other values without changing state. Shared IRQ filtering depends on enable and status bits being read consistently. Probe error paths return `-ENODEV` for several distinct failures.

## Test Signals
Test BAR mapping and sysfs map offsets/sizes, ADC and CTR4 interrupt filtering, userspace write-based irqcontrol, shared IRQ non-ownership, remove-time interrupt shutdown, and failure cleanup for partial BAR mapping or UIO registration failures.
