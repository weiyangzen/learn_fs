# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.h

## Purpose
`status-codes.h` reserves the VDO status-code block after the UDS block and declares all VDO-specific internal statuses plus registration and errno-conversion helpers.

## Important APIs, Types, And Functions
`enum vdo_status_codes` defines `VDO_STATUS_CODE_BASE`, specific failures such as `VDO_REF_COUNT_INVALID`, `VDO_NO_SPACE`, `VDO_READ_ONLY`, `VDO_CORRUPT_JOURNAL`, `VDO_JOURNAL_OVERFLOW`, and `VDO_INVALID_ADMIN_STATE`, then `VDO_STATUS_CODE_LAST` and `VDO_STATUS_CODE_BLOCK_END`. It declares `vdo_status_list[]`, `vdo_register_status_codes()`, and `vdo_status_to_errno()`.

## Control Flow
The header has no runtime control flow but establishes the numeric sequence used by `status-codes.c` and call sites throughout VDO.

## State And Persistence
These values are not directly on-disk records, but they are cross-component error contracts. Numeric stability matters for logging, registration, diagnostics, and any user-space code that decodes internal statuses.

## Dependencies And Integration Points
The header includes `errors.h` for the UDS error-block constants and `struct error_info`. Many VDO components include this header to return or test VDO-specific error results.

## Risks
Inserting, deleting, or reordering enum members changes numeric codes unless carefully coordinated. The block-size relationship with UDS errors must remain valid, and every enum value before `VDO_STATUS_CODE_LAST` needs a matching entry in `vdo_status_list[]`.

## Test Signals
Tests should assert numeric block boundaries, enum/list count parity, errno conversion for important statuses, and compilation of downstream modules that switch on these codes.
