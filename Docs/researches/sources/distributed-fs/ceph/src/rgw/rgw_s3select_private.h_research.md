# sources/distributed-fs/ceph/src/rgw/rgw_s3select_private.h

## Purpose
`rgw_s3select_private.h` declares the concrete S3 Select implementation and AWS event-stream response helper. It centralizes heavy dependencies on RGW S3 REST internals, the external s3select engine, liboath/auth headers, and optional Arrow/Parquet types so they stay out of the small public factory header.

## Important APIs, Types, and Functions
`aws_response_handler` owns event-stream payload buffers, CRC state, request/op pointers, usage counters, header constants, and chunked-transfer callback wiring. It declares methods to initialize records/progress/stats/end/error frames, create headers, send success/progress/stats/error responses, update bytes processed/returned, and choose main versus continuation buffers.

`RGWSelectObj_ObjStore_S3` derives from `RGWGetObj_ObjStore_S3`. It stores the parsed Select request XML, CSV/JSON/Parquet engine objects, delimiter/quote/escape/header options, scan range fields, progress flag, Trino flags, response handler, range-request scratch buffers, and callback functions for result formatting, continuation, debug logging, chunked encoding, range reads, and object size. It overrides `send_response_data()`, `get_params()`, and `execute()`.

## Control Flow
The concrete op behaves like a GET with a transform callback. `get_params()` parses the select request and then calls the base GET parameter setup. `execute()` initializes response handling and starts normal GET/range processing or Parquet reader-driven range processing. `send_response_data()` receives object bytes and dispatches to CSV, JSON, or Parquet processors.

## State and Persistence Behavior
All state is per-request and transient. The class tracks scan offsets, object size, whether a chunk should be skipped for Trino range alignment, continuation response buffers, and byte counters. It does not modify object attributes or bucket metadata.

## Dependencies and Integration Points
The header includes `rgw_rest_s3.h`, `rgw_s3select.h`, `s3select/include/s3select.h`, Boost CRC/tokenizer/string helpers, Ceph crypto/JSON/UTF-8 helpers, and optional Arrow-related Parquet declarations guarded by `_ARROW_EXIST`. It is only suitable for implementation files that can absorb those dependencies.

## Risks
The private class has many mutable request fields and callback functions, making reentrancy and partial-error behavior delicate. Header-level inclusion of several broad dependencies can increase compile sensitivity. The event-stream helper assumes the request state formatter and RGW op pointers are set before sending; `is_set()` guards that at runtime but does not enforce it statically.

## Test Signals
Tests should instantiate the concrete op through the public factory, validate callback initialization, exercise response-handler frame construction with CRCs, and cover mode flags for CSV, JSON, Parquet, scan ranges, progress, and Trino shaping.
