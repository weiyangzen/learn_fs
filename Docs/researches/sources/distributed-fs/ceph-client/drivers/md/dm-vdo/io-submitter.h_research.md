# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.h

## Purpose
`io-submitter.h` exposes the VDO I/O submitter abstraction and convenience wrappers for metadata and flush VIO submission.

## Important APIs, Types, and Functions
The header forward-declares `struct io_submitter` and declares create/cleanup/free functions plus data and metadata submission entry points. Inline helpers `vdo_submit_metadata_vio()`, `vdo_submit_metadata_vio_with_size()`, and `vdo_submit_flush_vio()` normalize common calls to `__submit_metadata_vio()`.

## Control Flow
Callers create the submitter during VDO setup, submit data VIOs through `vdo_submit_data_vio()`, submit metadata through the inline wrappers, optionally use the synchronous metadata wait helper early in startup, and finally cleanup/free during shutdown.

## State and Persistence Behavior
The header exposes no internals. All submitter state is runtime work-queue and merge-map state owned by the implementation. There is no persistence.

## Dependencies and Integration Points
It includes Linux `bio` declarations, VDO constants, and VDO types. Integration points include metadata subsystems that need physical block I/O and data paths that submit user data or compressed blocks.

## Risks and Edge Cases
The flush helper currently uses `REQ_OP_WRITE | REQ_PREFLUSH` with a FIXME asking whether plain `REQ_OP_FLUSH` is enough. Callers passing custom size/data must ensure buffers remain valid until completion.

## Test Signals
Compile coverage of inline wrappers and runtime tests for metadata read/write, custom-size metadata writes, flush submission, and early synchronous metadata reads are relevant.
