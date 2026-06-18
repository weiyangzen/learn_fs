# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-hvpipe.c

## Purpose
Implements `/dev/papr-hvpipe`, a userspace interface to the PAPR hypervisor pipe for inband communication with supported sources such as HMCs.

## Important APIs, Types, And Functions
The device ioctl path is `papr_hvpipe_dev_ioctl` and `papr_hvpipe_dev_create_handle`. Per-source file operations are `papr_hvpipe_handle_read`, `papr_hvpipe_handle_write`, `papr_hvpipe_handle_poll`, and `papr_hvpipe_handle_release`. RTAS wrappers are `rtas_ibm_receive_hvpipe_msg` and `rtas_ibm_send_hvpipe_msg`. Event handling uses `hvpipe_event_interrupt`, `papr_hvpipe_work_fn`, `set_hvpipe_sys_param`, `enable_hvpipe_IRQ`, and exported `hvpipe_migration_handler`.

## Control Flow
Init checks RTAS properties/tokens, allocates an ordered workqueue, registers the HVPIPE event IRQ, creates the miscdevice, and enables the firmware sysparm. Users open the miscdevice, issue create-handle ioctl with an HMC source id, then read/write/poll on the returned anonymous inode. Incoming event interrupts parse RTAS error-log HVPIPE sections, find a matching source, set status flags and wake waiters, or queue a worker to drain unmonitored messages. Reads return a small header plus payload and clear pending state; writes build a PAPR buffer-list and issue send.

## State And Persistence
Runtime state includes global source list, per-source waitqueues and status flags, global feature enable state, event buffer, workqueue, work item, and RTAS token. No durable filesystem state is written; firmware pipe enablement is controlled through a PAPR system parameter.

## Dependencies And Integration Points
Depends on RTAS send/receive/check-exception calls, RTAS work areas, PAPR sysparm, event-source IRQ registration, anonymous inodes, miscdevice, uapi HVPIPE structures, and mobility's suspend/resume notifications.

## Risks And Edge Cases
Only one process may own a source. If user space is not listening, messages are drained to avoid blocking the single partition pipe. Migration disables the feature and makes operations fail or poll hang up until resumed. User buffer sizes are capped to one 4048-byte payload plus header. Event parsing assumes the RTAS error log contains the HVPIPE section.

## Test Signals
Test miscdevice creation only when firmware advertises capability, create-handle validation, duplicate source rejection, read/write bounds, poll wakeups, lost-connection events, unmonitored message drain, release with pending payload, migration suspend/resume, and RTAS error mappings.
