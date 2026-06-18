# sources/distributed-fs/ceph-client/drivers/char/applicom.h

## Purpose

`applicom.h` defines the shared-memory register offsets and userspace-visible data layouts for the Applicom board driver. It is the protocol contract consumed by `applicom.c` and by user programs that read/write `/dev/ac`.

## Important APIs, Types, And Functions

The header defines no functions. Important constants are board RAM offsets such as `DATA_TO_PC_READY`, `DATA_FROM_PC_READY`, owner/destination TIC and card fields, `CONF_END_TEST`, `ERROR_CODE`, `PARAMETER_ERROR`, `VERS`, mailbox buffers `RAM_TO_PC`/`RAM_FROM_PC`, board identity fields, and interrupt bytes `RAM_IT_FROM_PC`/`RAM_IT_TO_PC`.

It defines two packed-by-layout C structs without explicit packing attributes:

- `struct mailbox`: command/status/user fields plus a 256-byte data payload; `applicom.c` transfers it byte-by-byte to and from board RAM.
- `struct st_ram_io`: a snapshot/control structure for low board RAM status bytes, identity/error fields, version, board number, and reserved data.

## Control Flow

There is no control flow. `applicom.c` uses the offsets for MMIO byte reads/writes in init, interrupt handling, read/write operations, and ioctl commands. Userspace buffer sizes are checked as `sizeof(struct st_ram_io) + sizeof(struct mailbox)`.

## State And Persistence Behavior

The header stores no state, but its offsets map directly to persistent board shared-memory state. Struct layout is ABI-relevant for `/dev/ac` read/write/ioctl behavior.

## Dependencies And Integration Points

It depends on fixed-width Linux integer typedefs being available through includers. It integrates with `applicom.c`, Applicom board firmware, and legacy userspace that builds buffers matching these structures.

## Risks And Edge Cases

The structs are not marked `__packed`; current field ordering likely avoids surprising padding for the intended ABI, but compiler/layout assumptions are still part of the contract. `NUMCARD_ACK_FROM_PC` is written as `0x010`, equivalent to `0x10`, which is visually easy to misread. Any offset change would break hardware protocol and userspace ABI. Endianness of multi-byte fields in `struct mailbox` is not converted by the driver.

## Test Signals

Compile ABI checks for `sizeof(struct st_ram_io)` and `sizeof(struct mailbox)` on supported architectures. Runtime tests should verify the driver's expected buffer length matches legacy userspace and that byte offsets read/write the intended board RAM locations.
