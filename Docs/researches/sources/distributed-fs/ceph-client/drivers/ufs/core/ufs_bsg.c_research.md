# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.c

## Purpose

`ufs_bsg.c` creates a block SCSI generic endpoint for raw UFS UPIU, UIC, task-management, query, NOP, and advanced RPMB requests.

## Important APIs, Types, and Functions

Public functions are `ufs_bsg_probe()` and `ufs_bsg_remove()`. Core handlers are `ufs_bsg_request()`, `ufs_bsg_alloc_desc_buffer()`, and `ufs_bsg_exec_advanced_rpmb_req()`.

## Control Flow

Probe initializes a child device named `ufs-bsgN` under the SCSI host and creates a bsg queue. Request handling resumes runtime PM, dispatches by `msgcode`, optionally allocates descriptor buffers for query descriptor reads/writes, calls raw UPIU or UIC helpers, handles advanced RPMB with DMA-mapped payloads and EHS validation, fills reply lengths, and completes successful jobs with `bsg_job_done()`. Remove tears down queue and device references.

## State and Persistence Behavior

Runtime state is `hba->bsg_dev` and `hba->bsg_queue`. Requests may mutate device state depending on raw UPIUs, query writes, UIC commands, or RPMB operations. No file-backed persistence is owned here.

## Dependencies and Integration Points

It depends on bsg-lib, DMA mapping, SCSI host device hierarchy, UFS raw command helpers, runtime PM, and advanced RPMB support in UFSHCI 4.0+ devices.

## Risks and Test Signals

Risks include user ABI exposure of low-level device commands, descriptor length validation mistakes, DMA map/unmap errors, completion only on success, advanced RPMB eligibility checks, and lifetime ordering for bsg device removal. Test signals include bsg node creation/removal, query read/write descriptor payloads, UIC command round trips, unsupported msgcodes, malformed advanced RPMB EHS/payloads, and runtime PM balancing.
