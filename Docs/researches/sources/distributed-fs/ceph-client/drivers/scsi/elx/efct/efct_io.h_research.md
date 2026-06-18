# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.h

## Purpose
`efct_io.h` defines the software IO object shared by unsolicited frame handling, SCSI target dispatch, LIO target glue, and HW submission. It also declares the IO pool APIs and target IO lookup helper.

## Important APIs, Types, and Functions
Key constants are `SCSI_CMD_BUF_LENGTH`, `SCSI_RSP_BUF_LENGTH`, and `EFCT_NUM_SCSI_IOS`. `enum efct_io_type` distinguishes SCSI IO, ELS, CT, BLS response, and abort software objects. `enum efct_els_state` tracks ELS request/abort states. `struct efct_io` is the central per-command object: it contains EFCT/node pointers, active/pending list links, kref, FC tags, software SGL, LIO private target IO, expected/transferred lengths, HW IO pointer, callback state, flags for target/initiator/abort behavior, HW IO parameters, response buffer DMA, timeout, priority, and app ID. `struct efct_io_cb_arg` carries generic completion status. Declared functions create/free pools, allocate/free IOs, count allocated entries, and find target IOs.

## Control Flow
Callers allocate `struct efct_io` from `efct_io_pool_io_alloc`, fill FC/SCSI/LIO fields, optionally associate a `struct efct_hw_io`, submit through `efct_scsi_io_dispatch`, then complete through SCSI/LIO callbacks and finally call `efct_scsi_io_complete` or pool free paths.

## State and Persistence Behavior
`struct efct_io` is reused across commands. Its DMA response buffer and SGL allocation persist for the lifetime of the pool, while command-specific fields must be reset before use. Krefs protect active command lifetime. The `io_free` flag is a defensive marker used to detect duplicate completion/free.

## Dependencies and Integration Points
The header includes `efct_lio.h`, which in turn includes SCSI target definitions. It references `efct_hw_io`, `efct_node`, `efct_scsi_sgl`, `efct_scsi_tgt_io`, and callback typedefs from the SCSI target layer. The dependency direction makes this file part of the tight SCSI/LIO/HW coupling.

## Risks
Because `struct efct_io` carries state for multiple protocols and phases, stale fields are a major risk if allocation reset misses a field. Including `efct_lio.h` from this generic IO header creates circular conceptual coupling. `EFCT_NUM_SCSI_IOS` is fixed at 8192 and can diverge from HW `n_io` if not considered by users.

## Test Signals
Compile tests should catch callback/type mismatches. Runtime checks should verify allocation reset coverage, response buffer sizing, SGL bounds, refcount transitions, duplicate-free detection, and IO reuse after abort or error completion.
