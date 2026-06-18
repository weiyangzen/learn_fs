# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.c

## Purpose
This file parses a text-form ZL3073x firmware bundle into named components, validates sizes and duplicates, and dispatches each component to the appropriate low-level flash operation.

## Important APIs and data
External APIs are `zl3073x_fw_load()`, `zl3073x_fw_free()`, and `zl3073x_fw_flash()`. `component_info[]` maps component IDs to names, maximum sizes, flash type, load address, destination page, and optional copy page. Flash types are none, sectors, page, and page-plus-copy.

## Control flow
`zl3073x_fw_load()` loops over the input buffer, calling `zl3073x_fw_component_load()` until no more component header can be parsed or an error occurs. A component header contains a name and word count; data follows as hexadecimal words. Unknown names, oversize components, duplicate components, missing data, and allocation failures abort and free prior components. `zl3073x_fw_flash()` iterates component IDs in fixed order and calls `zl3073x_fw_component_flash()`, which skips the utility component and otherwise chooses sectors/page/page+copy helpers from `flash.c`.

## State and persistence
Host-side firmware state is a heap-allocated `struct zl3073x_fw` with per-component buffers. It is freed after devlink flash update. Persistent effects occur only when flash helpers write device flash.

## Dependencies and integration points
It depends on `flash.c` for actual writes, `core.h` for device context, and devlink extack for user-facing parse/flash errors. `devlink.c` requires the utility component before entering flash mode.

## Risks and tests
The parser assumes text headers and hex words with whitespace; malformed or truncated input must not overrun the firmware buffer. Component order in the input is flexible, but duplicate IDs are rejected. Tests should cover unknown names, maximum-size boundaries, duplicate components, malformed hex, missing utility, page+copy components, and partial flash failure cleanup.
