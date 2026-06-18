# sources/distributed-fs/ceph-client/drivers/hid/hid-ids.h

Centralizes USB, Bluetooth, I2C, and virtual HID vendor/product IDs used by HID drivers and quirk tables. It is a shared compile-time registry rather than executable code.

The file defines preprocessor constants only, guarded by `HID_IDS_H_FILE`. In this work item it supplies identifiers for FT260, Gembird, Google Hammer/Stadia devices, GreenAsia, Gyration remotes, Holtek devices, ION iCade, Glorious mice, MSI GT683R, and Huawei CD30. These constants are consumed by match macros such as `HID_USB_DEVICE()`, `HID_BLUETOOTH_DEVICE()`, and `HID_DEVICE()`.

There is no runtime control flow or state. C preprocessing substitutes constants into match tables and quirk logic throughout `drivers/hid`. Changes alter compile-time binding behavior across all including drivers.

Risks include silent driver binding breakage if a constant is changed incorrectly, accidental reuse, and confusing duplicate vendor/product aliases where hardware is sold under multiple brands. Test signals are primarily build coverage, modalias/module autoload checks, expected runtime binding for affected devices, and reference searches to confirm constants are intentionally used.
