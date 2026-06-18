# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7x3x.c

## Purpose

This driver supports ADLINK PCI-723x and PCI-743x isolated digital I/O boards. It creates one or two DI/DO subdevices depending on board width and, for PCI-7230, optional async interrupt subdevices for isolated input channels 0 and 1 through a PLX9052 bridge.

## Important APIs, types, and functions

The board table `adl_pci7x3x_boards[]` defines subdevice count and DI/DO/IRQ channel counts. Private types are `adl_pci7x3x_dev_private_data` for PLX local config register base and interrupt control, and `adl_pci7x3x_sd_private_data` for per-interrupt-subdevice state. Important functions are `adl_pci7x3x_interrupt()`, `process_irq()`, `adl_pci7x3x_asy_cmdtest()`, `adl_pci7x3x_asy_cmd()`, `adl_pci7x3x_asy_cancel()`, DI/DO instruction handlers, `adl_pci7x3x_reset()`, and `adl_pci7x3x_auto_attach()`.

## Control Flow

Auto-attach selects board metadata, allocates device private data, enables PCI, records BAR 2 for DIO and BAR 1 for PLX local configuration, resets interrupts, optionally requests an IRQ for boards with interrupt channels, allocates the board-defined number of subdevices, and initializes DI and/or DO subdevices in 32-channel banks. For IRQ subdevices, it allocates subdevice private data, sets their source port offset, and installs command callbacks when IRQ setup succeeded. Async command start enables the matching PLX local interrupt line and marks the subdevice running. The ISR checks PLX LINT status bits, clears board interrupt flags, and calls `process_irq()` for subdevices 2 and 3.

## State and Persistence

State includes PLX interrupt control cache, per-subdevice command-running flags, DIO output state, and hardware PLX/DIO registers. There is no persistent storage. Detach resets PLX interrupt enables before generic PCI cleanup.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, `plx9052.h`, COMEDI async APIs, spinlocks, and ADLINK PCI IDs. It integrates hardware external interrupts into COMEDI async DI buffers.

## Risks

Interrupt support is documented as only currently supporting PCI-7230 despite board comments mentioning others. `dev->read_subdev` is overwritten for each IRQ subdevice, so generic fields only point to the last one even though the ISR directly indexes subdevices 2 and 3. DO handling for 16-channel PCI-7230 writes the state in both halves of a 32-bit register due to hardware behavior. Shared IRQ handling must ignore interrupts before `dev->attached`.

## Test Signals

Signals include correct subdevice layouts for all six boards, DI reads from low and high banks, DO writes for 16/32/64-channel boards, PCI-7230 interrupt commands on IDI0 and IDI1, cancel disabling PLX lines, shared IRQ rejection when LINT bits are not active, and detach clearing interrupt control.
