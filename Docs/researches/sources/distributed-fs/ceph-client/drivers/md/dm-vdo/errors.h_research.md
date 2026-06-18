# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.h

## Purpose
`errors.h` declares the UDS status-code namespace and the public error utility APIs used by the VDO indexer and kernel integration code.

## Important APIs, Types, And Functions
- `VDO_SUCCESS` and `UDS_SUCCESS` define zero success.
- `enum uds_status_codes` reserves the internal positive error block beginning at `UDS_ERROR_CODE_BASE == 1024`, including `UDS_OVERFLOW`, `UDS_INVALID_ARGUMENT`, `UDS_BAD_STATE`, `UDS_DUPLICATE_NAME`, `UDS_QUEUED`, `UDS_UNSUPPORTED_VERSION`, `UDS_CORRUPT_DATA`, `UDS_NO_INDEX`, and `UDS_INDEX_NOT_SAVED_CLEANLY`.
- `VDO_MAX_ERROR_NAME_SIZE` and `VDO_MAX_ERROR_MESSAGE_SIZE` size caller-provided formatting buffers.
- `struct error_info` pairs symbolic names with messages for built-in or registered error ranges.
- Public functions are `uds_string_error()`, `uds_string_error_name()`, `uds_status_to_errno()`, and `uds_register_error_block()`.

## Control Flow And Data Flow
Callers return positive UDS status codes inside the indexer and convert to kernel errno only at external boundaries. The header keeps status values contiguous so `errors.c` can index into `error_info` arrays by subtracting the block base.

## State And Persistence Behavior
The status-code values are ABI-like within this source tree and affect logs, saved error handling, and external failure semantics. They are not persisted directly by this header, but index-load decisions depend on distinguishing absent, corrupt, unclean, and unsupported index states.

## Dependencies And Integration Points
The header uses Linux compiler/types annotations and is included throughout the UDS indexer, assertion helpers, and VDO code paths that need to return or translate internal statuses. Registered blocks allow other modules to extend the error namespace without colliding with the built-in range.

## Risks
- Adding or reordering enum members changes numeric values unless new codes are appended before `UDS_ERROR_CODE_LAST`.
- `UDS_QUEUED` is a non-error status inside the same positive range, so callers must not blindly translate all positive results to failures.
- Registered block range arguments must be consistent with array sizes or unknown slots are exposed at runtime.

## Test Signals
Compile-time and runtime checks should verify stable numeric values, stringification for each enum, and caller handling of `UDS_QUEUED` as an asynchronous state rather than an error.
