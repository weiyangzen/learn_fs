# File Research: sources/block-storage/vdo/utils/vdo/status-codes.h

Declares the VDO status-code block.

Key details:
- Places VDO errors after the UDS error-code block.
- Enumerates VDO-specific errors from `VDO_NOT_IMPLEMENTED` through `VDO_NOT_READ_ONLY`.
- Exposes `vdo_status_list`, `vdo_register_status_codes()`, and `vdo_status_to_errno()`.

Research relevance:
- Shared error vocabulary across encoding, config, I/O, block-map, and stats utilities.
