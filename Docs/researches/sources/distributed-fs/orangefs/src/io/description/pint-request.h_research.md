# sources/distributed-fs/orangefs/src/io/description/pint-request.h

Purpose: declares the internal OrangeFS/PVFS request datatype model, request traversal state, result vectors, file distribution context, and macros used by request processing and flow protocols.

Important APIs/types: `PINT_Request` describes a datatype node with offset, element/block counts, stride, bounds, aggregate size, contiguous chunk count, nesting depth, packed/commit state, refcount, element request `ereq`, and sequence request `sreq`. `PINT_reqstack` and `PINT_Request_state` hold the iterative traversal cursor. `PINT_Request_result` carries output segment arrays and byte/segment limits. `PINT_request_file_data` binds a request to file size, current server number/count, distribution object, and extend policy. Public declarations include request state alloc/free, `PINT_process_request()`, `PINT_distribute()`, pack/encode/decode helpers, and dump helpers.

Control flow and state model: mode flags (`PINT_SERVER`, `PINT_CLIENT`, `PINT_CKSIZE`, `PINT_LOGICAL_SKIP`, `PINT_SEEKING`, `PINT_MEMREQ`) steer traversal and distribution behavior. Macros reset cursors, set target/final offsets, detect completion/EOF, compute pack sizes, and maintain request refcounts while preserving negative special-request refcounts.

Dependencies/integration: includes PVFS internal and type headers and forward-declares `PINT_dist_s`. The datatype constructors in `pvfs-request.c` populate this struct; `pint-request.c` executes it; flow descriptors hold `PINT_Request *file_req` and `*mem_req`.

Risks: macros evaluate pointer fields directly and do not validate inputs. Refcount macros intentionally skip negative static/packed requests but do not recursively free. `PINT_REQUEST_STATE_RESET()` currently matches `RST()` and does not alter target/final offsets despite comments implying start reset semantics. Tests should validate macro behavior on static elementary requests, packed requests, reset/resume cursors, and aggregate/contiguous statistics consumed by flow code.
