# sources/distributed-fs/ceph-client/include/uapi/linux/nvram.h

Purpose: Defines the small `/dev/nvram` ioctl ABI and offset helper constants for legacy system NVRAM access.

Important APIs/types/functions: Exports `NVRAM_INIT`, `NVRAM_SETCKS`, `NVRAM_FIRST_BYTE`, and `NVRAM_OFFSET(x)`.

Control flow: Userspace can ask the driver to initialize NVRAM and set the checksum, or recalculate the checksum after modifications. Data reads/writes use NVRAM offsets relative to `NVRAM_FIRST_BYTE` rather than absolute platform byte positions.

State and persistence behavior: NVRAM is persistent firmware/platform storage. This header does not store data but defines operations that can update persistent checksum-covered bytes.

Dependencies and integration points: Depends on `<linux/ioctl.h>`. Integrates with architecture-specific NVRAM drivers, boot variables, and old platform configuration tools.

Risks: Incorrect offset calculation can corrupt firmware settings. Init and checksum ioctls mutate persistent state and should be access-controlled. The constant assumes current systems expose NVRAM starting at byte 14.

Test signals: Exercise read/write/checksum tools on emulated or disposable NVRAM, verify `NVRAM_OFFSET()` conversions, reject invalid offsets in the driver, and ensure checksum recalculation survives reboot.
