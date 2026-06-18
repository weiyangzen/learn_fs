# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/status-codes.c

## Purpose
`status-codes.c` registers VDO-specific status codes with the shared UDS error framework and maps internal VDO/UDS/system errors to kernel errno return values.

## Important APIs, Types, And Functions
`vdo_status_list[]` provides names and messages for each `enum vdo_status_codes` value. `vdo_register_status_codes()` validates list length with `BUILD_BUG_ON()` and registers the block. `vdo_status_to_errno()` normalizes successful, negative errno, small positive errno, and VDO/UDS status codes.

## Control Flow
Registration is a simple one-shot call into `uds_register_error_block()`. Error mapping returns existing non-positive values unchanged, maps positive values below 1024 to negative errno, maps `VDO_BAD_CONFIGURATION` to `-EINVAL`, `VDO_NO_SPACE` to `-ENOSPC`, `VDO_READ_ONLY` to `-EIO`, and logs any other internal status before returning `-EIO`.

## State And Persistence
No persistent state is written. The status-code numeric range is ABI-like because error names, messages, and mappings are consumed across VDO and UDS components.

## Dependencies And Integration Points
The file depends on `errors.h`, `logger.h`, `permassert.h`, and `thread-utils.h`. It integrates with UDS error registration and the kernel-facing paths that must return negative errno values.

## Risks
If the enum and `vdo_status_list[]` diverge, registration would describe the wrong errors; the compile-time size assertion mitigates this. Unknown errors are intentionally collapsed to `-EIO`, so losing a specific mapping can reduce diagnosability or alter user-visible behavior.

## Test Signals
Tests should verify registration size, all status-to-string entries, direct errno passthrough, positive errno negation, specific VDO mappings, and default logging-to-`-EIO` behavior.
