# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_realtek.h

## Purpose

`unusual_realtek.h` lists Realtek card-reader devices that use the Realtek-specific initialization path.

## Important APIs, Types, and Functions

The file contributes six `UNUSUAL_DEV()` rows for VID `0x0bda` products `0x0138`, `0x0153`, `0x0158`, `0x0159`, `0x0177`, and `0x0184`. Rows use device-reported subclass/protocol and call `init_realtek_cr`.

## Control Flow

Macro expansion lets the generic ignore table decline these devices or lets the Realtek subdriver claim them. For matching devices, `init_realtek_cr` runs before command processing to set up reader-specific behavior.

## State and Persistence Behavior

The header stores no state. Runtime state is created by the Realtek initializer and associated subdriver cleanup.

## Dependencies and Integration Points

It depends on `init_realtek_cr`, Realtek card-reader support, and macro-table inclusion by `usual-tables.c` or the subdriver. It integrates with usb-storage probe and SCSI media scanning.

## Risks and Edge Cases

All entries cover all firmware revisions. This is convenient for reused Realtek reader IDs but may be too broad if a future revision becomes generic-compatible. Missing a new product ID would leave it on the generic path without Realtek setup.

## Test Signals

Compile Realtek reader support, verify ID-table expansion, attach each supported product family, test media insertion/removal, suspend/resume, and disconnect cleanup.
