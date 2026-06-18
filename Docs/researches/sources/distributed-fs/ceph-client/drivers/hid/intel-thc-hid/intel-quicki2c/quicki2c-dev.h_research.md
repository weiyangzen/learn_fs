# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-dev.h

## Purpose
`quicki2c-dev.h` defines QuickI2C platform IDs, ACPI method names and function numbers, timing limits, runtime-PM defaults, the QuickI2C state enum, ACPI buffer structures, platform data, and the main `struct quicki2c_device`.

## Important APIs, types, and functions
Constants cover LNL/PTL/WCL/NVL PCI device IDs, HIDI2C DSD methods `ICRS` and `ISUB`, DSM function numbers for HID descriptor address and LTR values, I2C speed thresholds, default LTR and autosuspend values, RX max-detect limits, interrupt-delay limits, and addressing modes. `struct quicki2c_subip_acpi_parameter` describes ICRS data; `struct quicki2c_subip_acpi_config` describes ISUB timing and DMA-advanced controls. `struct quicki2c_ddata` stores platform RX-detection capabilities. `struct quicki2c_device` is the complete PCI device context.

## Control flow and integration points
The header has no executable control flow. `pci-quicki2c.c` fills the device context from PCI and ACPI, protocol code consumes descriptors/buffers/THC handles, and HID glue stores `hid_dev` and uses descriptor fields for HID registration.

## State and persistence behavior
It defines volatile per-device runtime state: ACPI parameters, MMIO, THC/HID/ACPI pointers, buffers, wait queues, reset flag, advanced DMA settings, LTR values, and current state. No persistent storage is defined.

## Dependencies
It includes HID-over-I2C protocol types and Linux workqueue declarations, and forward-declares PCI, ACPI, THC, HID, and device structures. It relies on shared THC constants for I2C mode values in implementation files.

## Risks and edge cases
Packed ACPI structures must match platform firmware exactly. Many ACPI timing fields are `u64` but are later assigned into `u32` device fields, so large values can truncate. PCI ID constants must stay aligned with the PCI match table. Buffer length/report length fields come from device descriptors and need defensive allocation in implementation code.

## Test signals
Compile coverage, ACPI fixture parsing for ICRS/ISUB, platform data selection by PCI ID, max-detect clamping, waitqueue/reset state behavior, and suspend/resume tests using the stored LTR/timing fields are relevant signals.
