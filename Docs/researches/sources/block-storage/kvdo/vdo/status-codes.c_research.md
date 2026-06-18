# File Research: sources/block-storage/kvdo/vdo/status-codes.c

This file defines VDO error metadata and maps internal status codes to OS errno values. `vdo_status_list[]` mirrors `enum vdo_status_codes` and is checked with a static assertion against the enum range.

`vdo_register_status_codes()` uses `perform_once()` to register the VDO error block with the shared UDS error registry. Duplicate registration is treated as success to support statically linked test/module scenarios where multiple copies call registration against shared libuds state.

`vdo_map_to_system_error()` normalizes errors for kernel return paths:
- `0` or already-negative errno values pass through.
- Small positive errno macros are negated.
- `VDO_NO_SPACE` maps to `-ENOSPC`.
- `VDO_READ_ONLY` maps to `-EIO`.
- Other VDO/UDS codes are logged with name/message and mapped to `-EIO`.
