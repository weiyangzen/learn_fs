# sources/distributed-fs/ceph-client/drivers/usb/storage/uas-detect.h

## Purpose

`uas-detect.h` contains shared UAS detection helpers used by both `uas.c` and `usb.c`. It decides whether an interface can and should bind to the UAS driver instead of falling back to classic `usb-storage`, including endpoint validation and bridge-specific quirks.

## Important APIs, Types, and Functions

`uas_is_interface()` recognizes mass-storage/SCSI/UAS alternate settings. `uas_find_uas_alt_setting()` scans a USB interface for such an alternate setting. `uas_find_endpoints()` parses endpoint extra descriptors with `USB_DT_PIPE_USAGE` and maps command, status, data-in, and data-out endpoints. `uas_use_uas_driver()` combines alternate-setting discovery, endpoint presence, device quirks, module `quirks=` overrides via `usb_stor_adjust_quirks()`, HCD scatter-gather support, and SuperSpeed streams support.

## Control Flow

When `usb-storage` probes a device, it calls `uas_use_uas_driver()` and declines binding if UAS is viable. When `uas.c` probes, the same helper must return true before the driver switches the interface to the UAS alternate setting. The helper first checks descriptors, then applies known ASMedia, Seagate, Realtek/HIKSEMI, and user-supplied quirks, then rejects UAS if `US_FL_IGNORE_UAS` is set, scatter-gather is unsupported, or SuperSpeed streams are required but unavailable.

## State and Persistence Behavior

The helpers do not persist state. They compute a `u64` flags value returned to the caller and may emit warnings. Runtime state such as selected alternate setting, allocated streams, and SCSI host data is created later by `uas.c`.

## Dependencies and Integration Points

The file depends on USB descriptors, HCD capabilities, UAS pipe-usage descriptors, `usb.h`, and `usb_stor_adjust_quirks()`. It is an integration point between the legacy usb-storage driver and the UAS driver, preventing both from binding to the same capable interface.

## Risks and Edge Cases

Endpoint extra descriptor parsing assumes sane descriptor lengths; malformed descriptors with zero length could cause parser trouble in USB descriptor walking. ASMedia detection uses power, speed, product IDs, and stream counts as heuristics because IDs are reused. String-based HIKSEMI detection depends on manufacturer/product strings being present and exact. Overriding flags through the `quirks=` parameter can force fallback or remove safeguards.

## Test Signals

Test UAS-capable devices with and without all four pipe-usage endpoints, USB2 and SuperSpeed ASMedia bridges, Seagate enclosures, RTL9210/HIKSEMI MD202 strings, HCDs without SG, HCDs without streams, and module quirk overrides that add or remove `US_FL_IGNORE_UAS`.
