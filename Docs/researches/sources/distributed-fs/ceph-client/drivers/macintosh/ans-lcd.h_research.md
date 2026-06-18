# sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.h

Purpose: provides the private ioctl command numbers used by the Apple Network Server LCD driver. It is intentionally small and only defines the ABI selectors consumed by `ans-lcd.c`.

Important APIs and types: defines `ANSLCD_CLEAR`, `ANSLCD_SENDCTRL`, `ANSLCD_SETSHORTDELAY`, and `ANSLCD_SETLONGDELAY` as integer command values `0x01` through `0x04`. The include guard is `_PPC_ANS_LCD_H`.

Control flow: none in this header. Consumers include it and switch on the constants in their file operation ioctl path.

State and persistence: no state. The constants are ABI-facing because userspace code can issue them to `/dev/anslcd`.

Dependencies and integration: integrated directly with `ans-lcd.c`. No kernel headers are included beyond the SPDX and guard.

Risks: these are not `_IO`, `_IOR`, or `_IOW` encoded ioctl numbers, so command typing, size validation, and namespace collision protection are absent. Changing any numeric value would break existing userspace tools for this device.

Test signals: build coverage should confirm the header is included by `ans-lcd.c`. ABI tests should verify each constant still triggers the expected behavior in the driver.
