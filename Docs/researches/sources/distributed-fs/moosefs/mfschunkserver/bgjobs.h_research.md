# sources/distributed-fs/moosefs/mfschunkserver/bgjobs.h

## Purpose
`bgjobs.h` is the public interface for the chunkserver background job subsystem. It exposes asynchronous job submission APIs, cancellation/callback mutation, load reporting, chunk operation convenience macros, and initialization.

## Important APIs
`job_stats` returns and resets the maximum observed job count for charting. `job_get_load_and_hlstatus` returns current total queued/running load and high-load status. `job_pool_disable_job` disables a pending job, while `job_pool_change_callback` changes its completion callback and extra pointer.

`job_chunkop` is the generic disk chunk mutation submission function, parameterized by `chunkid`, current version, new version, optional copy chunk/version, and length. Macros map common operations to that shape: `job_delete`, `job_create`, `job_test`, `job_version`, `job_truncate`, `job_duplicate`, `job_duptrunc`, and `job_split`. Some macros validate arguments and route invalid requests to `job_inval`.

Client service work is submitted with `job_serv_read` and `job_serv_write`; replication work with `job_replicate_simple`, `job_replicate_split`, `job_replicate_recover`, and `job_replicate_join`; metadata/info work with `job_get_chunk_info` and convenience macros for blocks, checksum, and checksum tables; disk relocation with `job_chunk_move`. `job_init` starts the subsystem and registers it with the main event loop.

## Control Flow and Integration
Callers enqueue jobs and receive a numeric job id. Completion is asynchronous through `void (*callback)(uint8_t status, void *extra)`. The callback status uses MooseFS protocol status/error constants from `MFSCommunication.h`. The service layer (`csserv.c`) stores returned job ids so it can disable jobs when a connection closes. Master and disk-management code use chunk-operation and replication APIs to avoid blocking the event loop.

## State and Persistence
This header declares no state; all state is owned by `bgjobs.c`. Jobs are volatile and not replayed after process restart. The pointer arguments passed as callback extras remain caller-owned unless the implementation explicitly frees its internal argument blocks.

## Dependencies
The header includes `MFSCommunication.h` for constants such as `MAX_EC_PARTS`, `REQUEST_BLOCKS`, `REQUEST_CHECKSUM`, and error/status codes. It includes `<inttypes.h>` for fixed-width integer types.

## Risks
The macros encode sentinel values (`0xFFFFFFFF`, `0x80000000`) that must match `hdd_chunkop` semantics. Callers must check for job id zero on limited-return APIs such as service read/write because zero means the job was not queued. Callback extras must remain valid until callback or explicit callback removal. Replication arrays must contain at least `parts` valid entries and must not exceed `MAX_EC_PARTS`.

## Test Signals
Compilation across all include sites is a basic API compatibility signal. Runtime tests should assert invalid macro inputs produce `MFS_ERROR_EINVAL`, service APIs return zero under configured saturation, and cancellation/callback mutation through a stored job id prevents callbacks from dereferencing closed connection state.
