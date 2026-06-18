<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h

## Purpose
This header provides tagged command queue lookup support for SCSI hosts using blk-mq tags.

## Important APIs, Types, And Functions
It defines `SCSI_NO_TAG` and, when `CONFIG_BLOCK` is enabled, inline `scsi_host_find_tag(struct Scsi_Host *shost, int tag)`. The helper decodes a unique blk-mq tag into hardware queue and per-queue tag, looks up the request from the host tag set, verifies the request has started, and returns the embedded `struct scsi_cmnd`.

## Control Flow
Callers pass a tag from an active command or task-management context. The helper rejects `SCSI_NO_TAG`, rejects hardware queue indices outside the tag set, rejects missing or not-started requests, and otherwise converts request private data back into a SCSI command.

## State And Persistence
No state is owned. It reads the live `Scsi_Host::tag_set` and active request state.

## Dependencies And Integration Points
It depends on block, SCSI command/device/host headers, and blk-mq unique tag helpers. It is used by LLDDs and EH/TMF code that need to find an outstanding command from a tag.

## Risks
Tags are only valid while the request is active. Multi-queue tags must be unique blk-mq tags, not raw hardware tags. Concurrent completion can race lookup, so callers need appropriate context/lifetime protection.

## Test Signals
Test `SCSI_NO_TAG`, invalid hardware queue tags, inactive requests, valid single-queue and multi-queue tags, and races with command completion under lockdep/KCSAN-style checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_tcq.h -->
