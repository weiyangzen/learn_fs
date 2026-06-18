# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.h

## Purpose
Declares common wlcore boot entry points and firmware static-data constants/layout.

## Important APIs, types, and functions
- `wlcore_boot_upload_firmware()`, `wlcore_boot_upload_nvs()`, and `wlcore_boot_run_firmware()` are exported boot-stage helpers used by lower drivers.
- `struct wl1271_static_data` mirrors firmware static data: MAC address, firmware version string, hardware version, TX power table, and lower-driver private tail.
- Constants define power-table dimensions, firmware-version string length, init polling loop/delay, and ELP/wake command values.

## Control flow
No executable flow. Lower-driver boot implementations call the three boot helpers in chip-specific order.

## State and persistence behavior
No local state. The static-data structure describes volatile firmware-provided data read during boot.

## Dependencies and integration points
Includes wlcore core definitions. Implemented by `boot.c` and called from chip-family `main.c` files such as wl18xx.

## Risks and test signals
ABI mismatch in `wl1271_static_data` breaks firmware-version validation and lower-driver private static data parsing. Boot tests should verify firmware upload, NVS upload, firmware run, static-data parsing, and init-complete timing on supported chips.
