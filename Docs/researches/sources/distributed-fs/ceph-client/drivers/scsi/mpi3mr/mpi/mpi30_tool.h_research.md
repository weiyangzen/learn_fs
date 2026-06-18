# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_tool.h

Purpose: declares the MPI3 diagnostic buffer post/manage protocol used to hand host diagnostic buffers to firmware and later release, pause, resume, or clear them.

Important APIs/types/functions: defines diagnostic buffer types `MPI3_DIAG_BUFFER_TYPE_TRACE` and `MPI3_DIAG_BUFFER_TYPE_FW`, management actions `MPI3_DIAG_BUFFER_ACTION_RELEASE`, `PAUSE`, `RESUME`, and `CLEAR`, the segmented-post message flag, `struct mpi3_diag_buffer_post_request`, and `struct mpi3_diag_buffer_manage_request`.

Control flow: `mpi3mr_app.c` allocates trace/FW host diagnostic buffers, fills a post request with buffer type, DMA address, length, and segmented flag, then waits for admin completion. Release uses the manage request with release action and updates local HDB status based on completion or diagnostic-buffer status-change events.

State and persistence behavior: this header stores no state. The protocol mutates firmware ownership of host diagnostic buffers; local status is tracked in `struct diag_buffer_desc` as not allocated, posted/unpaused, posted/paused, or released. Buffer contents persist in host memory until uploaded by BSG or freed during cleanup.

Dependencies and integration points: included by `mpi3mr.h`; uses MPI transport function IDs `MPI3_FUNCTION_DIAG_BUFFER_POST` and `MPI3_FUNCTION_DIAG_BUFFER_MANAGE` from `mpi30_transport.h`. Tied to IOC facts diagnostic size/capability fields, Driver Page 1 sizing, Driver Page 2 trigger policy, HDB BSG commands, and firmware event `MPI3_EVENT_DIAGNOSTIC_BUFFER_STATUS_CHANGE`.

Risks and test signals: main risks are DMA address/length endian mistakes, segmented trace buffer list handling, posting buffers larger than controller limits, and stale local status after firmware releases/pauses a buffer. Tests should cover contiguous and segmented trace posting, FW buffer posting, release timeout/reset handling, BSG query/upload/repost, and status-change event reasons released/paused/resumed/cleared.
