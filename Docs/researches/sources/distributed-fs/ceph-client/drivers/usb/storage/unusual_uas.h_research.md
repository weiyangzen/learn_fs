# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_uas.h

## Purpose

`unusual_uas.h` is the UAS-specific quirk table. It lists USB storage devices that advertise UAS but need flags such as disabling UAS, limiting command size, avoiding ATA pass-through, disabling FUA, suppressing REPORT OPCODES/LUNS, or forcing sync-cache behavior.

## Important APIs, Types, and Functions

The file contains 23 `UNUSUAL_DEV()` rows and intentionally requires the includer to define `UNUSUAL_DEV`. Rows mostly use `USB_SC_DEVICE` and `USB_PR_DEVICE` because they augment matching devices rather than selecting a nonstandard usb-storage transport. Important flags include `US_FL_IGNORE_UAS`, `US_FL_NO_REPORT_OPCODES`, `US_FL_NO_SAME`, `US_FL_NO_REPORT_LUNS`, `US_FL_NO_ATA_1X`, `US_FL_IGNORE_RESIDUE`, `US_FL_BROKEN_FUA`, and `US_FL_ALWAYS_SYNC`.

## Control Flow

`uas.c` expands the file into `uas_usb_ids[]`, before the generic mass-storage UAS/BOT interface matches. During probe, `uas_use_uas_driver()` starts with `id->driver_info`, applies dynamic heuristics and user quirks, and may reject UAS if `US_FL_IGNORE_UAS` is set. If UAS binds, `uas_sdev_configure()` translates flags into SCSI device behavior such as queue limits, broken FUA, no report opcodes, no write same, capacity heuristics, and cache page handling.

## State and Persistence Behavior

The file stores no state. It determines per-device quirk flags copied into `struct uas_dev_info`. Those flags persist only for the device lifetime and affect SCSI queue/device configuration.

## Dependencies and Integration Points

It depends on UAS driver ID-table expansion, usb-storage quirk definitions, and shared detection in `uas-detect.h`. It integrates with both bind selection and SCSI device configuration.

## Risks and Edge Cases

UAS quirk policy is especially sensitive because devices often advertise UAS despite broken firmware. A missing `US_FL_IGNORE_UAS` can expose data-corrupting command sequencing; an unnecessary one reduces performance by forcing BOT. Flags that suppress REPORT OPCODES, FUA, SAME, or ATA pass-through can hide features but improve compatibility.

## Test Signals

Validate each listed device or bridge family for binding/fallback, command queueing, large transfer limits, FUA/write-cache behavior, REPORT LUNS/OPCODES handling, ATA passthrough, and BOT fallback when `US_FL_IGNORE_UAS` is present.
