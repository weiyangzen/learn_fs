# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_devlink.c

## Purpose
`es58x_devlink.c` provides product metadata parsing and devlink info reporting for ETAS ES58x adapters. It extracts firmware version, bootloader version, and hardware revision from a USB product information string, then exposes those values plus the USB serial number through devlink.

## Important APIs, Types, And Functions
The main exported items are `es58x_parse_product_info()` and `const struct devlink_ops es58x_dl_ops`. Internal helpers are `es58x_parse_sw_version()`, `es58x_parse_hw_rev()`, `es58x_sw_version_is_valid()`, `es58x_hw_revision_is_valid()`, and `es58x_devlink_info_get()`. The product info string index is `ES58X_PROD_INFO_IDX` with value 6.

## Control Flow
During probe, the core calls `es58x_parse_product_info()`. The function initializes version/revision fields to invalid sentinel values, retrieves USB string index 6 with `usb_cache_string()`, then attempts to parse firmware (`FW`), bootloader (`BL`), and hardware revision fields. Parsing is tolerant of two known software prefixes (`FW_Vxx.xx.xx`/`BL_Vxx.xx.xx` and `FW:xx.xx.xx`/`BL:xx.xx.xx`) by searching for the prefix and then the first digit. Hardware parsing searches for the only `H`, then the next colon, and scans an `axxx/xxx` revision. Failures log informational messages but do not abort device probe.

When users request devlink info, `es58x_devlink_info_get()` validates each parsed field. Valid firmware and bootloader versions are reported as running generic firmware and bootloader versions, valid board revision is reported as a fixed board revision, and the USB serial string is reported as the serial number.

## State And Persistence
No independent state is allocated here. The file mutates fields in `struct es58x_device`: `firmware_version`, `bootloader_version`, and `hardware_revision`. Those values live for the USB device lifetime and are not persisted beyond driver unload or unplug.

## Dependencies And Integration Points
This file depends on Linux USB string retrieval, character classification, devlink info APIs, and `struct es58x_device` from `es58x_core.h`. It is linked into the same module and its `es58x_dl_ops` pointer is passed to `devlink_alloc()` in the core.

## Risks
Parsing is based on vendor-specific free-form strings and is intentionally non-fatal. New firmware string formats may result in missing devlink version fields while the CAN driver still works. Sentinel values use unsigned fields assigned `-1`, and validity checks rely on them exceeding the maximum printable range. The hardware parser assumes the only relevant `H` belongs to the hardware revision prefix, which could fail for unexpected strings.

## Test Signals
Use devices or mocked USB descriptors with both known string formats, missing product info, malformed versions, malformed hardware revisions, and serial/no-serial cases. Verify `devlink dev info` shows firmware, bootloader, board revision, and serial only when parsed values are valid, and that probe continues when parsing fails.
