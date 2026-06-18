# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.c

## Purpose
This file initializes HPI message and response buffers with the correct size, type, object, function, version, adapter index, and default error values before dispatch.

## Important APIs, Types, And Functions
The exported functions are `hpi_init_response()`, `hpi_init_message_response()`, `hpi_init_responseV1()`, and `hpi_init_message_responseV1()`. Static helpers `hpi_init_message()` and `hpi_init_messageV1()` do the request side. `msg_size[]` and `res_size[]` derive object-specific sizes from `HPI_MESSAGE_SIZE_BY_OBJECT` and `HPI_RESPONSE_SIZE_BY_OBJECT`.

## Control Flow
For normal messages, object indexes in range are masked with `array_index_nospec()` before indexing the size arrays; invalid objects fall back to the full generic structure size. Message buffers are zeroed only to the selected message size, while responses are zeroed across `sizeof(*phr)` and then record the selected response size. Paired initializers create a request and a response whose default error is `HPI_ERROR_PROCESSING_MESSAGE`.

## State, Persistence, And Dependencies
Persistent state is limited to static size tables and `gwSSX2_bypass`, which selects `HPI_TYPE_SSX2BYPASS_MESSAGE` instead of `HPI_TYPE_REQUEST`. The code depends on `hpi_internal.h`, `hpimsginit.h`, and Linux `nospec` helpers.

## Integration Points
Every HPI API wrapper, ioctl request, probe path, and message router uses these initializers to guarantee predictable headers and safe default failure responses.

## Risks
The bypass flag is file-static and has no setter in this file, so behavior is effectively fixed unless changed elsewhere at link time. V1 message initialization silently leaves fields zeroed if the object is out of range. The request zero length follows per-object size, so incorrect size tables could leave stale bytes in larger unions if callers later use the wrong object payload.

## Test Signals
Tests should validate header fields for normal and V1 requests, invalid object fallback behavior, default error propagation when lower layers do not fill a response, and nospec-protected object indexes at bounds.
