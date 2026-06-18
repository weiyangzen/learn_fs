# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar71xx.c

## Purpose
Implements Atheros AR71xx PCI host controller config access, reset, resource registration, and chained interrupt handling.

## Important APIs, Types, And Functions
Defines `struct ar71xx_pci_controller`, `ar71xx_pci_ops`, `ar71xx_pci_probe`, `ar71xx_pci_reset`, IRQ chip callbacks, and `postcore_initcall(ar71xx_pci_init)`.

## Control Flow
Probe maps the config register block and resources, resets PCI bus/core through ATH79 reset helpers, programs the local PCI command register, clears bus errors, installs IRQ chips for the ATH79 PCI IRQ range, fills the PCI controller, and registers it. Config reads/writes build type-0/type-1 addresses, program byte-lane enables, check PCI/AHB error registers, and access config read/write data registers. Chained IRQ handling reads ATH79 reset interrupt pending/enabled bits and dispatches device/core IRQs.

## State And Persistence
State is per-controller in the platform device object: resource descriptors, IRQ base, and config base. Hardware reset, command, error, and interrupt-enable registers are modified during boot and IRQ operations.

## Dependencies And Integration Points
Depends on ATH79 reset/DDR helpers, platform resources `cfg_base`, `io_base`, `mem_base`, and Linux PCI/IRQ APIs.

## Risks And Edge Cases
Byte-lane table has BUG_ON for invalid size/offset combinations. Error handling logs critical bus errors when not quiet. IRQ dispatch uses an else-if chain, so one parent interrupt handles one pending source at a time. Reset timing uses fixed delays.

## Test Signals
AR71xx board boot, PCI device config scanning, AHB/PCI error clearing, interrupt delivery for DEV0-2 and CORE, and build coverage for `CONFIG_SOC_AR71XX` are relevant.
