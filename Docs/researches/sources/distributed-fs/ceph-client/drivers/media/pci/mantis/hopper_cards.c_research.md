# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_cards.c

## Purpose
This file is the PCI driver for Hopper bridge based DVB cards, currently wiring the Twinhan VP-3028 DVB-T board to the shared Mantis core.

## Important APIs, Types, and Functions
Key elements are module parameter `verbose`, `hopper_irq_handler`, `hopper_pci_probe`, `hopper_pci_remove`, the `hopper_pci_table`, and `hopper_pci_driver`. The probe path uses `struct mantis_pci`, `struct mantis_pci_drvdata`, and `struct mantis_hwconfig`.

## Control Flow
Probe allocates `mantis_pci`, copies PCI/config data, installs the Hopper IRQ handler into the hardware config, initializes core PCI resources, sets stream routing to HIF, initializes I2C, reads the MAC, initializes DMA, and registers DVB. Error paths unwind in reverse. The IRQ handler reads interrupt status/mask, handles GPIF/CA events, UART, RISC DMA blocks, I2C completion, error bits, clears status, and schedules bottom halves or wakes waitqueues.

## State and Persistence Behavior
The driver stores per-device state in `struct mantis_pci`, including interrupt status/mask, GPIF status, busy DMA block, adapter state, RC map, and core subsystem allocations. The global `devs` count assigns device numbers and `verbose` controls logging.

## Dependencies and Integration Points
It depends on PCI module infrastructure, shared Mantis PCI/I2C/DMA/DVB/UART/IOC code, Hopper VP-3028 config, Mantis register access macros, CA/HIF waitqueues/work items, and DVB demux/frontend registration.

## Risks
IRQ handling assumes `mantis->mantis_ca` is valid when IRQ0 fires. Probe error labels must match initialization order; early failures after `mantis_stream_control` jump to PCI teardown without a separate stream undo. Interrupt mask manipulation must be protected by `intmask_lock` for IRQ1. Device count is not decremented on remove.

## Test Signals
PCI probe/remove, IRQ storm handling, I2C completion waits, DMA RISC block delivery, CA IRQ0 events, UART IRQ1 work scheduling, frontend attach through VP-3028 config, and failure injection at each probe stage are useful.
