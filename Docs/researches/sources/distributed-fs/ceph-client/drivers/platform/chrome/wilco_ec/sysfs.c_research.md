<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c

## Purpose

This file exposes Wilco EC platform settings and information through sysfs attributes on the core Wilco EC device.

## Important APIs, Types, And Functions

Attributes include write-only `boot_on_ac`, read-only `version`, `build_revision`, `build_date`, `model_number`, and read/write `usb_charge`. `get_info()` sends command `0x38` for EC strings. `boot_on_ac_store()` sends legacy CMOS auto-on command `0x7c/0x03`. `send_usb_charge()`, `usb_charge_show()`, and `usb_charge_store()` implement command `0x39`. `wilco_ec_add_sysfs()` and `wilco_ec_remove_sysfs()` manage the group.

## Control Flow

Core probe calls `wilco_ec_add_sysfs()`. Show/store methods parse or format values, build packed legacy request/response structs, and call `wilco_ec_mailbox()`. Stores accept boolean-like numeric values 0 or 1. Remove deletes the attribute group.

## State And Persistence

No values are cached. Reads fetch current EC data; writes update EC-controlled behavior. `boot_on_ac` and USB charge settings may persist in EC/firmware storage depending on platform implementation.

## Dependencies And Integration Points

It depends on the Wilco mailbox API, sysfs, and the documented Wilco EC ABI. It is linked into the core module.

## Risks

EC info strings may be non-NUL-terminated and are printed with a fixed width, which is correct but can include padding. Store methods accept only decimal 0/1. Any EC status byte for USB charge is collapsed to `-EIO`.

## Test Signals

Test sysfs group presence, each info attribute, valid and invalid store values, EC command failure paths, USB charge status failure, and teardown after open sysfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c -->
