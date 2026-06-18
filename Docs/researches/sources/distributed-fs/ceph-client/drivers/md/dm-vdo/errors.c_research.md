# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/errors.c

## Purpose
`errors.c` implements UDS/VDO error-code stringification, kernel errno translation, and registration of additional error-code blocks. It bridges internal positive UDS status codes with negative Linux errno values expected by kernel callers.

## Important APIs, Types, And Functions
- `message_table[]` provides fixed text for common errno values up to `ERANGE`.
- `error_list[]` defines built-in UDS status names/messages for codes beginning at `UDS_ERROR_CODE_BASE`.
- `struct error_block` describes a registered range, and `registered_errors` stores up to `MAX_ERROR_BLOCKS` ranges.
- `get_error_info()` resolves an error code to an `error_info` and optional block name.
- `uds_string_error()` formats a human-readable message.
- `uds_string_error_name()` formats a stable symbolic name.
- `uds_status_to_errno()` converts UDS status values to negative kernel errno values.
- `uds_register_error_block()` adds non-overlapping custom error-code ranges.

## Control Flow And Data Flow
Stringification normalizes negative inputs to positive codes, looks for registered UDS-style ranges, and falls back to the errno message table. Known internal codes are formatted as either `block: message` or symbolic names; reserved but undefined slots are reported as unknown codes inside the block. Unknown system errors are rendered into the caller buffer by `system_string_error()`.

`uds_status_to_errno()` treats zero and negative values as already kernel-compatible. Positive values below 1024 are assumed to be userspace errno numbers and negated. Internal UDS codes are mapped case-by-case: missing/corrupt index to `-ENOENT`, incompatible or unclean saved index to `-EEXIST`, disabled sessions to `-EIO`, and unexpected internal errors to `-EIO` with an informational log.

## State And Persistence Behavior
The module has process-global mutable state in `registered_errors`. It is not persisted to disk. Error text is static and used for diagnostics only. The mappings affect externally visible error behavior for index load/create paths, especially preventing an existing but unsupported index from being mistaken for absent.

## Dependencies And Integration Points
The file uses `logger.h` for fallback mapping logs, `permassert.h` for range validation, and `string-utils.h` for bounded appends. UDS indexer code returns these positive status values; kernel-facing VDO paths call `uds_status_to_errno()` when reporting failures to block/device-mapper layers.

## Risks
- `registered_errors` has no explicit locking. It is safe only if registrations happen during initialization or otherwise serialized.
- `uds_string_error_name()` lacks the explicit `buf == NULL` guard present in `uds_string_error()`.
- Positive values below 1024 are treated as errno values, so accidental internal codes in that range would be translated incorrectly.
- The static errno table is partial; unknown errno values get generic formatting rather than kernel `strerror` behavior.

## Test Signals
Unit-style tests should cover negative errno passthrough, positive errno translation, every special `uds_status_to_errno()` mapping, unknown internal errors and logs, buffer truncation behavior, duplicate block names, overlapping ranges, and registration capacity overflow.
