# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.h

## Purpose

This header defines the public in-kernel PMT telemetry endpoint interface used by clients that need to enumerate, register, inspect, and read PMT telemetry endpoints.

## Important APIs, Types, And Functions

It defines telemetry type constants `PMT_TELEM_TELEMETRY` and `PMT_TELEM_CRASHLOG`, `struct telem_header`, and `struct telem_endpoint_info`. It declares `pmt_telem_get_next_endpoint()`, `pmt_telem_register_endpoint()`, `pmt_telem_unregister_endpoint()`, `pmt_telem_get_endpoint_info()`, `pmt_telem_find_and_register_endpoint()`, `pmt_telem_read()`, and `pmt_telem_read32()`.

## Control Flow

The intended flow is: iterate endpoint IDs, fetch endpoint info if needed, register an endpoint to increment its kref, perform aligned sample reads by sample ID, and unregister when done. `pmt_telem_find_and_register_endpoint()` combines lookup by device, GUID, and instance position.

## State And Persistence

The header owns no state. It documents that endpoint pointers carry a kref in the implementation and that `-ENODEV` from reads indicates a removed endpoint requiring unregister.

## Dependencies And Integration Points

The declarations are implemented by `pmt/telemetry.c` and used by PMT telemetry consumers. The API exposes only opaque `struct telem_endpoint *` plus endpoint metadata.

## Risks

The comments say `pmt_telem_read32()` reads qwords even though it operates on dwords; this documentation mismatch can confuse callers. The API relies on callers to allocate sufficiently large buffers and request in-bounds aligned sample ranges.

## Test Signals

Compile tests for telemetry consumers, endpoint enumeration tests, and read-path tests for invalid IDs, removed endpoints, and out-of-range offsets validate the contract.
