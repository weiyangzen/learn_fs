# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/s3fwrn5.h

## Purpose
`s3fwrn5.h` defines the shared Samsung S3FWRN5 core contract between physical layers, firmware code, and NCI glue.

## Important APIs and types
- `enum s3fwrn5_mode` defines COLD, NCI, and firmware modes.
- `struct s3fwrn5_phy_ops` abstracts wake, mode set/get, and write operations supplied by physical layers.
- `struct s3fwrn5_info` stores the NCI device, physical id, parent device, physical ops, firmware state, and core mutex.
- Inline wrappers `s3fwrn5_set_mode()`, `s3fwrn5_get_mode()`, `s3fwrn5_set_wake()`, and `s3fwrn5_write()` validate operation presence and call through to the transport.
- Prototypes expose shared probe/remove and inbound frame routing.

## Control flow and integration
Physical drivers call `s3fwrn5_probe()` and provide `s3fwrn5_phy_ops`; the core uses inline wrappers everywhere else. Receive paths in transports call `s3fwrn5_recv_frame()` with the current mode.

## State and persistence
The header describes in-memory runtime state only. Firmware persistence is represented indirectly through `struct s3fwrn5_fw_info`.

## Dependencies and risks
It depends on Linux NFC/NCI types and `firmware.h`. The inline `s3fwrn5_get_mode()` returns `-EOPNOTSUPP` through an enum return type when missing, so all physical ops should be complete. The `set_wake` argument is named `sleep` in the function pointer but used as wake semantics by callers, which can confuse maintainers.

## Test signals
Build tests should catch missing physical ops. Runtime tests should verify each physical implementation obeys the mode/wake/write contract expected by `core.c` and `firmware.c`.
