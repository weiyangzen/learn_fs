# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_status.h

## Purpose

`core_status.h` centralizes Display Core status/error codes and string conversion helpers. The enum values identify validation, resource-allocation, bandwidth, link, DSC, cursor, and unexpected failure outcomes.

## Important APIs, Types, And Functions

`enum dc_status` defines `DC_OK`, resource failures for controllers, encoders, clocks, DSC, and link encoders, validation failures for controller/encoder/surface/bandwidth/scaling/DSC/link bandwidth/tunnel bandwidth/cursor support, clock min/max failures, unsupported/value errors, DP training/payload failures, and `DC_ERROR_UNEXPECTED`. Helpers are `dc_status_to_str`, `dc_pixel_encoding_to_str`, and `dc_color_depth_to_str`.

## Control Flow

Display validation and commit functions return `enum dc_status` to short-circuit unsuccessful modes or resource mappings. Diagnostic paths convert status, pixel encoding, and color depth values to strings for logging.

## State And Persistence Behavior

The header has no state. Status values propagate through call stacks and may be recorded in logs or validation results owned by callers.

## Dependencies And Integration Points

It includes `dc_hw_types.h` for pixel-encoding and color-depth enums. It is used by resource validation, HWSS context application, clock programming, link training, DSC allocation, and public DC APIs that need stable status reporting.

## Risks And Edge Cases

Numeric enum values are explicit and may be externally observed in logs or tooling; renumbering is risky. `DC_OK` starts at 1 while `DC_ERROR_UNEXPECTED` is -1, so code must not treat zero as success. New validation failures need string mappings to avoid opaque logs.

## Test Signals

Builds catch missing enum types. Unit/log tests should verify every status maps to a meaningful string and failure paths preserve the precise status. Integration tests should cover bandwidth, DSC, link bandwidth, link training, payload allocation, and clock-limit failure propagation.
