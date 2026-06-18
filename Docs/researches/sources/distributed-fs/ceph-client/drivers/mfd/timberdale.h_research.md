# sources/distributed-fs/ceph-client/drivers/mfd/timberdale.h

## Purpose
`timberdale.h` defines firmware compatibility constants, register offsets, BAR-relative child resource offsets, PCI IDs, IRQ indices, GPIO pins, and DMA channel numbers for the Timberdale FPGA MFD driver.

## Important APIs, Types, and Functions
Key constants include `DRV_VERSION`, `TIMB_SUPPORTED_MAJOR`, `TIMB_REQUIRED_MINOR`, control registers `TIMB_REV_MAJOR`, `TIMB_REV_MINOR`, `TIMB_HW_CONFIG`, `TIMB_SW_RST`, hardware config masks, BAR offset/end pairs, `PCI_VENDOR_ID_TIMB`, `PCI_DEVICE_ID_TIMB`, `IRQ_TIMBERDALE_*`, `TIMBERDALE_NR_IRQS`, GPIO pins, and DMA channel identifiers.

## Control Flow
There is no executable control flow. `timberdale.c` consumes these constants to validate firmware, map control registers, select child cell configuration, and assign resources.

## State and Persistence
The header defines static constants only. Firmware revision and hardware config values are read at runtime by the driver.

## Dependencies and Integration Points
It is private to the Timberdale MFD driver and aligns resource numbers with child platform drivers for DMA, media, networking, GPIO, SPI, I2C, UART, and SDHCI blocks.

## Risks and Edge Cases
Incorrect offsets or IRQ indices would misroute child MMIO or MSI-X interrupts. The firmware support window is encoded here, so driver updates are required for newer major versions.

## Test Signals
Compile coverage and runtime resource verification for every hardware config exercise this header. Firmware compatibility tests should confirm the major/minor constants match intended support.
