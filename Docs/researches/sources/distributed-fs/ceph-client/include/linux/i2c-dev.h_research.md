# sources/distributed-fs/ceph-client/include/linux/i2c-dev.h

## Purpose
Provides the in-kernel wrapper for the userspace I2C character-device UAPI and defines the I2C char-device major number.

## APIs, Control Flow, and State
The header includes `<uapi/linux/i2c-dev.h>` and defines `I2C_MAJOR` as 89. It has no functions or local state; actual char-device control flow is implemented by the i2c-dev driver and UAPI ioctl definitions.

## Dependencies, Integration, Risks, and Tests
Depends on the exported UAPI header. Integrates with `/dev/i2c-*` nodes, userspace ioctl clients, and device-number registration. Risks are ABI mismatch with UAPI definitions or incorrect assumptions that this header implements device operations. Test signals include i2c-dev module/device creation, major number registration, and ioctl compatibility tests.
