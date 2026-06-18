# sources/distributed-fs/ceph-client/drivers/staging/greybus/firmware.h

## Purpose
Shared private header for the Greybus firmware bundle implementation. It centralizes firmware naming constants and cross-file entry points for firmware management, firmware download, component authentication, and optional SPI support through the core firmware bundle driver.

## Important APIs, Types, And Functions
Defines `FW_NAME_PREFIX` and `FW_NAME_SIZE`, used by firmware download to construct deterministic firmware filenames. Declares `fw_mgmt_init()/fw_mgmt_exit()`, `gb_fw_mgmt_request_handler()`, `gb_fw_mgmt_connection_init()/exit()`, `gb_fw_download_request_handler()`, `gb_fw_download_connection_init()/exit()`, and CAP equivalents. `to_fw_mgmt_connection()` exposes the management connection from a device.

## Control Flow
This header has no runtime control flow, but it defines the contract used by `fw-core.c` to initialize per-protocol connections after parsing bundle CPorts. Request handlers declared here are passed into `gb_connection_create()` for management and download protocols.

## State And Persistence
No state is stored here. The constants shape persistent user-visible firmware lookup names, using interface and product identifiers plus a short tag.

## Dependencies And Integration Points
Includes `<linux/greybus.h>` because all declared connection and operation types are Greybus core structures. It is included by `fw-core.c`, `fw-download.c`, and `fw-management.c`.

## Risks
`FW_NAME_SIZE` must remain synchronized with the formatting string in `fw-download.c`; an undersized constant would truncate firmware names. The header is an internal coupling point, so changing prototypes affects multiple protocol modules.

## Test Signals
Build coverage is the main signal. Firmware download tests should verify generated names fit exactly within `FW_NAME_SIZE`; firmware core tests should catch missing declarations or mismatched prototypes.
