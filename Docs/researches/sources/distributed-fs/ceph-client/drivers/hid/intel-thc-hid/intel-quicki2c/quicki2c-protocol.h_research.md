# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.h

## Purpose
`quicki2c-protocol.h` declares the QuickI2C HID-over-I2C protocol operations used by PCI probe/PM code and HID low-level callbacks.

## Important APIs, types, and functions
It declares `quicki2c_set_power()`, `quicki2c_get_report()`, `quicki2c_set_report()`, `quicki2c_output_report()`, `quicki2c_get_device_descriptor()`, `quicki2c_get_report_descriptor()`, and `quicki2c_reset()`, and forward-declares `struct quicki2c_device`.

## Control flow and integration points
There is no executable control flow. `pci-quicki2c.c` uses descriptor, reset, power, and report-descriptor functions during probe and PM. `quicki2c-hid.c` uses GET/SET/output functions for HID raw requests.

## State and persistence behavior
The header owns no state. Declared functions operate on volatile `quicki2c_device` state and buffers.

## Dependencies
It includes Linux HID-over-I2C for `enum hidi2c_power_state` and report constants used by callers.

## Risks and edge cases
Signature drift can break the HID and PCI layers. Since the header exposes raw buffer pointers and lengths, callers must provide buffers that match HID/core expectations and device report framing.

## Test signals
Build coverage, probe descriptor/reset flow, HID raw request paths, and PM power-state calls validate this contract.
