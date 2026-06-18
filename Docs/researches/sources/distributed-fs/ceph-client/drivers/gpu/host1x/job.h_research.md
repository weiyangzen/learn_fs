<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h

## Purpose

`job.h` defines internal host1x job command descriptors and unpin records used by job pinning and channel submission.

## Important APIs, Types, And Functions

- `struct host1x_job_gather`: gather word count, DMA base, BO pointer, byte offset, and duplicate-handled flag.
- `struct host1x_job_wait`: syncpoint ID, threshold, next class, and relative/absolute mode.
- `struct host1x_job_cmd`: tagged union of gather or wait command.
- `struct host1x_job_unpin_data`: BO mapping to release after completion.
- `host1x_job_dump()` emits debug details for a job.

## Control Flow

The header has no direct flow. `job.c` appends commands, `channel_hw.c` consumes them in order, and CDMA completion calls unpin.

## State And Persistence Behavior

These descriptors persist inside `struct host1x_job` while the job is pending. Submission mutates gather base/handled fields and wait thresholds may be interpreted relative to syncpoint max.

## Dependencies And Integration Points

Depends on DMA direction types and public host1x BO/job structures from includers. It is shared by job, CDMA, channel, and debug code.

## Risks And Test Signals

The `is_wait` tag must match the union member. Tests that mix waits and gathers, duplicate gather BOs, and relative waits validate the descriptor contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h -->
