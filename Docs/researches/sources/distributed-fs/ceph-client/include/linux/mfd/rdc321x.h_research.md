# sources/distributed-fs/ceph-client/include/linux/mfd/rdc321x.h

## Purpose
`rdc321x.h` provides shared definitions for the RDC321x southbridge MFD children, specifically GPIO and watchdog blocks implemented as offsets in PCI configuration space.

## Important APIs, Types, And Constants
The header defines config-register offsets for watchdog control, GPIO control/data register pairs, and `RDC321X_NUM_GPIO` set to 59. `struct rdc321x_gpio_pdata` passes a southbridge `struct pci_dev *` and maximum GPIO count to the GPIO child. `struct rdc321x_wdt_pdata` passes the same PCI device to the watchdog child.

## Control Flow And State
The MFD core owns discovery of the southbridge PCI device and instantiates GPIO/watchdog children with platform data. Children use `sb_pdev` to read/write PCI config offsets such as `RDC321X_GPIO_CTRL_REG1`, `RDC321X_GPIO_DATA_REG1`, `RDC321X_GPIO_CTRL_REG2`, `RDC321X_GPIO_DATA_REG2`, and `RDC321X_WDT_CTRL`.

## State And Persistence Behavior
State is in PCI configuration registers, not in this header. GPIO direction/data and watchdog control affect hardware immediately and may persist until reset depending on chipset behavior. Platform data stores only pointers and bounds.

## Dependencies And Integration Points
The file depends on Linux types and PCI declarations. It integrates with the PCI core, MFD platform-device creation, GPIO subsystem, and watchdog subsystem.

## Risks
Accessing PCI config registers through a shared southbridge device requires careful serialization in child drivers. `max_gpios` must not exceed the hardware count. Wrong offsets can affect unrelated southbridge functions because this is not a normal MMIO register block.

## Test Signals
Tests should verify child devices receive a valid PCI device, GPIO count is clamped to 59, register offsets match chipset documentation, watchdog enable/disable works, and GPIO control/data operations do not corrupt adjacent PCI config fields.
