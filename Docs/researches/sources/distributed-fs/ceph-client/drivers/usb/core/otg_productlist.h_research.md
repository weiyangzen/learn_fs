# sources/distributed-fs/ceph-client/drivers/usb/core/otg_productlist.h

## Purpose
Defines the OTG/embedded-host Targeted Peripheral List used to decide whether a connected USB device is supported by a constrained OTG host product.

## Important APIs, Types, And Functions
The file declares `productlist_table[]` of `struct usb_device_id` entries and defines `is_targeted(struct usb_device *dev)`. Entries are conditionally compiled for hubs, printers, CDC Ethernet gadgets, RNDIS gadgets, and USB test gadget zero. It also hard-codes OTG special cases for the HNP test device and OTG PET device.

## Control Flow
`is_targeted()` rejects the HNP test device, accepts the OTG PET device, then manually walks `productlist_table` because interface caches are not available at this point. It checks vendor, product, device revision range, device class, subclass, and protocol match flags. If no entry matches, it logs an unsupported device error and returns false.

## State And Persistence
The product list is static compile-time data. There is no runtime mutation or persistence. Build-time Kconfig options alter the accepted table.

## Dependencies And Integration Points
Depends on USB device ID matching macros and descriptor fields. It is intended to be included by OTG/embedded-host code rather than compiled as a standalone C file. Its result gates whether an OTG host accepts or rejects a peripheral.

## Risks And Test Signals
Risks include stale product policy, incorrect manual matching behavior versus `usb_match_id()`, build-option-dependent acceptance, and noisy rejection logging for products that should be supported. Test signals include matching each conditional entry, HNP/PET special-case behavior, revision-bound entries if added, and negative tests for unsupported devices.
