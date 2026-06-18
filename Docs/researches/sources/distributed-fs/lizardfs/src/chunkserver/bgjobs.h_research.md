# sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.h

## Purpose
`bgjobs.h` declares the public background job pool API used by chunkserver code to offload blocking HDD and replication work.

## Important APIs, Types, And Functions
- Pool lifecycle: `job_pool_new`, `job_pool_jobs_count`, `job_pool_check_jobs`, and `job_pool_delete`.
- Job management: `job_pool_disable_and_change_callback_all`, `job_pool_disable_job`, and `job_pool_change_callback`.
- Generic/compound chunk operation enqueueing: `job_inval` and `job_chunkop`.
- Convenience macros: `job_delete`, `job_create`, `job_test`, `job_version`, `job_truncate`, `job_duplicate`, and `job_duptrunc`; invalid inputs become `job_inval`.
- I/O jobs: `job_open`, `job_close`, `job_read`, `job_prefetch`, `job_write`, and `job_get_blocks`.
- Replication jobs: `job_replicate`, `job_legacy_replicate`, and `job_legacy_replicate_simple`.

## Control Flow
Callers create a pool with a worker count and queue capacity, then use returned `wakeupdesc` in their event loop. Each submitter receives a job id and later receives `callback(status, extra)` when `job_pool_check_jobs` drains completions. Macro wrappers validate required version/copy/length parameters before enqueueing state-changing chunk operations.

## State And Persistence
The header exposes opaque `void *jpool` handles and raw callback/context pointers. Persistence is delegated to the underlying HDD operations; the API itself only manages asynchronous state.

## Dependencies And Integration Points
It includes `OutputBuffer` for reads and `ChunkPartType` via `common/chunk_type_with_address.h`. It is the integration boundary between connection/master command handling and chunkserver storage operations.

## Risks
- The API is C-style and pointer-heavy; buffer and output-pointer lifetimes are caller responsibility.
- Macros evaluate some arguments more than once in conditions or function arguments, so side-effect expressions would be unsafe.
- `void *` erases type safety for pools and callback context.

## Test Signals
No direct header tests are listed. API behavior is verified only if implementation/integration tests cover all job macros and callback paths.
