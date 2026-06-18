# sources/distributed-fs/orangefs/src/io/job/job.h

## Purpose
`job.h` declares the public OrangeFS job API. It gives server and client code a single asynchronous operation contract for network, storage, flow, scheduler, device, null, and precreate-pool work.

## Important APIs and types
`job_id_t` is an id-generator-backed operation id, and `job_context_id` identifies one completion queue slot. `JOB_MAX_CONTEXTS` limits concurrent job contexts to 16. `job_status_s` is the common completion payload: it always carries `status_user_tag` and `error_code`, and conditionally carries actual byte count, vtag, iterator position, created handle, verified type, collection id, and item count.

Management APIs are `job_initialize()`, `job_finalize()`, `job_open_context()`, `job_close_context()`, and `job_reset_timeout()`. Posting APIs are grouped by subsystem: BMI send/receive/unexpected/cancel, client device unexpected/write, request scheduler post/mode/timer/release, `job_flow()`, a large TROVE storage set, `job_null()`, and precreate-pool helpers. Completion APIs are `job_test()`, `job_testsome()`, and `job_testcontext()`.

## Control flow and contract
Post functions follow the same contract documented by implementation comments: return `1` when the job completed immediately and `out_status_p` is valid, return `0` when the caller must later test the returned id, and return negative errors for some unsupported or setup failures. The completion APIs populate arrays of returned user pointers and statuses, with `job_test()` acting as a single-id wrapper around `job_testsome()`.

## State and persistence behavior
This header does not hold state, but its API exposes the stateful parts of the implementation: contexts, job ids, timeout-managed operations, and status fields that reflect lower-layer persistent TROVE operations. The precreate-pool functions expose a server-side cache/allocation layer over stored handle pools.

## Dependencies and integration points
The header includes flow descriptors, BMI types, PVFS core types, `pvfs2-storage.h`, request protocol and scheduler types, and `pint-dev`. That makes it a high-fan-in interface between state machines and lower I/O subsystems.

## Risks
The API is broad and relies on callers knowing which `job_status_s` fields apply to which operation. The return convention can be easy to misuse because negative returns and immediate error completions are both possible depending on function/build path. `JOB_MAX_CONTEXTS` is fixed, and there is no type-level separation between job ids from different subsystems.

## Test signals
Header-level compatibility tests should compile representative callers for every declared family, assert expected status fields for each operation type, and check that unsupported build configurations still expose declarations while returning the documented runtime error.
