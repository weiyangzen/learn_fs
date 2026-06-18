# sources/distributed-fs/ceph-client/include/uapi/linux/sonypi.h

## Purpose
Defines the legacy Sony Programmable I/O control userspace ABI for VAIO hotkey, jog dial, battery, brightness, Bluetooth, fan, and temperature events exposed by `/dev/sonypi`.

## Important APIs, Types, and Constants
The header exports event numbers from `SONYPI_EVENT_IGNORE` through `SONYPI_EVENT_VENDOR_PRESSED`, including jog dial, Fn key, capture, wireless, lid, memory stick, battery, volume, and media-button events. Ioctls include `SONYPI_IOCGBRT`, `SONYPI_IOCSBRT`, `SONYPI_IOCGBAT1CAP`, `SONYPI_IOCGBAT1REM`, `SONYPI_IOCGBAT2CAP`, `SONYPI_IOCGBAT2REM`, `SONYPI_IOCGBATFLAGS`, `SONYPI_IOCGBLUE`, `SONYPI_IOCSBLUE`, `SONYPI_IOCGFAN`, `SONYPI_IOCSFAN`, and `SONYPI_IOCGTEMP`. Battery flag bits are `SONYPI_BFLAGS_B1`, `SONYPI_BFLAGS_B2`, and `SONYPI_BFLAGS_AC`.

## Control Flow, State, and Persistence
Event delivery occurs through device reads. Ioctls query or mutate firmware-backed device state such as brightness and radio/fan state. Numeric event assignments are persistent ABI for user daemons.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl encoding provided by consumers. Integrates with the sonypi driver, laptop hotkey daemons, and older VAIO platform control tools.

## Risks and Test Signals
Risks include stale hardware-specific semantics, obsolete event values that must stay reserved, and privilege/safety concerns around fan or wireless control. Test by compiling old sonypi userspace, checking ioctl sizes for `__u8` and `__u16`, and using driver or mock tests for event decoding and state query/set round trips.
