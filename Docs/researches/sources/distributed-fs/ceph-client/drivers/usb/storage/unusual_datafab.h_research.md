# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_datafab.h

## Purpose

`unusual_datafab.h` lists Datafab and compatible flash readers that require the `USB_PR_DATAFAB` usb-storage protocol transport. These devices historically use nonstandard command handling and are kept out of the generic mass-storage path.

## Important APIs, Types, and Functions

The file contains ten `UNUSUAL_DEV()` rows, mostly VID `0x07c4` product variants plus one compatible ID. Rows set `USB_SC_SCSI`, `USB_PR_DATAFAB`, no initializer, and in selected cases `US_FL_SINGLE_LUN`.

## Control Flow

Macro expansion inserts these IDs into ignore or specialized subdriver tables. During probe, a matching device is associated with Datafab command handling; if `US_FL_SINGLE_LUN` is present, the SCSI scan is constrained to LUN 0.

## State and Persistence Behavior

The header persists no state. It shapes in-memory probe configuration: protocol, transport, flags, vendor/product strings, and LUN policy.

## Dependencies and Integration Points

It depends on the macro-table pattern used by `usual-tables.c` and the Datafab subdriver. It integrates with usb-storage quirk flags and SCSI LUN scanning decisions.

## Risks and Edge Cases

The first row covers a narrow bcd range while many later rows cover all revisions. That split must reflect real firmware behavior. Wrong `US_FL_SINGLE_LUN` use could hide media slots or cause invalid LUN probing on fragile readers.

## Test Signals

Validate ID-table generation, probe routing to the Datafab transport, LUN behavior on single- and multi-slot readers, and media read/write across represented product IDs.
