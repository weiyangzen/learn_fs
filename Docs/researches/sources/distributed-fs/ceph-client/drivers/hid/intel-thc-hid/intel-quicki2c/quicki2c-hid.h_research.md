# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.h

## Purpose
`quicki2c-hid.h` is the small public declaration header for QuickI2C HID-core integration.

## Important APIs, types, and functions
It forward-declares `struct quicki2c_device` and declares `quicki2c_hid_send_report()`, `quicki2c_hid_probe()`, and `quicki2c_hid_remove()`.

## Control flow and integration points
There is no executable control flow. The PCI driver calls probe/remove, and the IRQ data path calls `quicki2c_hid_send_report()` when HIDI2C input data is available. Protocol/HID code share `struct quicki2c_device` through the forward declaration.

## State and persistence behavior
The header owns no state; the implementation stores HID registration state in `quicki2c_device`.

## Dependencies
It depends only on the QuickI2C device type existing in implementation files. The minimal include surface helps avoid HID header leakage.

## Risks and edge cases
Signature drift between this header and `quicki2c-hid.c` would break callers. There is no compile-time visibility into report buffer size semantics beyond `size_t data_size`.

## Test signals
Build coverage for PCI, HID, and protocol objects; HID probe/remove flow; and input-report forwarding through this declared API are the main signals.
