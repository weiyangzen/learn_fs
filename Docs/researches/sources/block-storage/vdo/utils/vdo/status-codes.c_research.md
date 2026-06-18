# File Research: sources/block-storage/vdo/utils/vdo/status-codes.c

Registers VDO-specific status codes and maps internal errors to OS errno values.

Key details:
- Defines `vdo_status_list[]` names/messages for all VDO errors.
- `vdo_register_status_codes()` registers the VDO error block once using `vdo_perform_once()`.
- Duplicate registration is treated as success for static-link scenarios where multiple objects register the same block.
- `vdo_status_to_errno()` returns existing negative errors unchanged, maps small positive errno values to negative errno, maps `VDO_NO_SPACE` to `-ENOSPC`, maps `VDO_READ_ONLY` to `-EIO`, and logs/defaults other VDO/UDS errors to `-EIO`.

Research relevance:
- Bridges internal userspace/kernel-style status codes to system-facing error returns.
