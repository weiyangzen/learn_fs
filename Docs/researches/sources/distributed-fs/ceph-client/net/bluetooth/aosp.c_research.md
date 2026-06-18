# sources/distributed-fs/ceph-client/net/bluetooth/aosp.c

## Purpose
This file implements support for Android Open Source Project Bluetooth vendor extensions, currently focused on discovering vendor capabilities and enabling/disabling Bluetooth Quality Report events.

## Important APIs, Types, And Functions
`aosp_do_open()` queries vendor capabilities with OGF 0x3f/OCF 0x153 and records quality-report support. `aosp_do_close()` is a cleanup hook. `aosp_has_quality_report()` exposes capability state. `aosp_set_quality_report()` selects `enable_quality_report()` or `disable_quality_report()`, which send the BQR vendor command OGF 0x3f/OCF 0x015e using `struct aosp_bqr_cp`.

## Control Flow
On HCI open, the file first checks `hdev->aosp_capable`, sends the get-capabilities command synchronously, validates the returned buffer size against versioned layouts, logs the vendor capability version, rejects versions below 0.95, requires v0.98 for quality reports, and sets `hdev->aosp_quality_report` when the controller reports support. Enabling BQR sends an ADD action with default event mask and interval; disabling sends a CLEAR action.

## State, Persistence, And Dependencies
State is stored on `struct hci_dev` as `aosp_capable` and `aosp_quality_report`. There is no persistence beyond the HCI device lifetime. The file depends on synchronous HCI command helpers, Bluetooth device logging, little-endian conversions, and vendor command semantics.

## Integration Points
The Makefile includes this object under `CONFIG_BT_AOSPEXT`. HCI core open/close and management paths call the declared hooks through `aosp.h`, and users of quality reporting call `aosp_set_quality_report()` after capability discovery.

## Risks
Vendor response layout grows over time, so length checks must stay version-aware. The code initializes `event_mask` and `min_report_interval` in host-endian fields inside a packed command struct; this relies on the expected command endianness and could be fragile across architecture review. A typo in macro names does not affect behavior but makes audits harder. Synchronous command failures only log and leave the feature disabled.

## Test Signals
Signals include HCI open on AOSP-capable controllers logging version, controllers below v0.98 not exposing BQR, BQR enable/disable sending the expected vendor command, malformed short capability responses logging length errors without memory access, and `aosp_has_quality_report()` matching controller support.
