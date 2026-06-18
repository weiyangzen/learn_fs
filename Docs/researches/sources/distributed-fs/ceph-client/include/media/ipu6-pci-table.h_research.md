# sources/distributed-fs/ceph-client/include/media/ipu6-pci-table.h

## Purpose
Provides PCI ID table entries and device-data references for Intel IPU6-family PCI camera devices.

## Important APIs, Types, and Functions
The header defines IPU6 PCI device IDs and table rows mapping them to IPU6 device data used by the PCI driver.

## Control Flow
The PCI core matches device IDs against the table, then the driver uses the associated data to select IPU6 variant behavior.

## State and Persistence Behavior
No runtime state is owned; the table is compile-time driver match data.

## Dependencies and Integration Points
Integrates Intel IPU6 PCI probe with kernel PCI matching and variant-specific media driver data.

## Risks
Wrong ID-to-data mapping can bind a supported device with incompatible register/firmware assumptions or fail to bind a valid platform.

## Test Signals
PCI modalias matching, probe on each listed IPU6 variant, lspci ID checks, and build coverage when variant data changes.
