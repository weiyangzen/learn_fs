# File Research: sources/block-storage/kvdo/vdo/errors.h

## Purpose
Defines UDS status codes, error metadata shape, and conversion/registration APIs.

## Main Contents
- `enum uds_status_codes`: success plus internal error codes starting at 1024.
- Reserved block end `UDS_ERROR_CODE_BLOCK_END` leaves room for future UDS errors.
- Error string buffer size constants.
- `struct error_info`: symbolic name and human message.

## API
- `uds_string_error()`
- `uds_string_error_name()`
- `uds_map_to_system_error()`
- `register_error_block()`

## Integration
Shared by low-level UDS structures such as delta index, geometry, buffers, and by higher VDO paths that must return Linux-compatible errno values.
