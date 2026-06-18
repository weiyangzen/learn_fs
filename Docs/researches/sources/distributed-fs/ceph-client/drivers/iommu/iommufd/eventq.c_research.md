# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/eventq.c

## Purpose
This file implements IOMMUFD event queues backed by anon inodes. It supports page-fault queues for I/O page faults and vIOMMU event queues for driver-reported virtual IOMMU events, including read/write/poll/release file operations and object lifecycle cleanup.

## Important APIs, Types, And Functions
Fault handling includes `iommufd_fault_alloc()`, `iommufd_fault_iopf_handler()`, `iommufd_fault_fops_read()`, `iommufd_fault_fops_write()`, `iommufd_fault_destroy()`, and `iommufd_auto_response_faults()`.

vEVENTQ handling includes `iommufd_veventq_alloc()`, `iommufd_veventq_abort()`, `iommufd_veventq_destroy()`, `iommufd_veventq_fops_read()`, and helper fetch/restore functions.

Common infrastructure includes `iommufd_eventq_init()`, `iommufd_eventq_fops_poll()`, `iommufd_eventq_fops_release()`, and the `INIT_EVENTQ_FOPS` macro.

## Control Flow
Fault allocation validates flags, allocates an IOMMUFD fault object, initializes a response xarray and mutex, creates an anon inode with read/write/poll ops, responds to userspace with object ID and fd, then installs the fd. Hardware page faults arrive through `iommufd_fault_iopf_handler()`, which appends an `iopf_group` to the deliver list and wakes readers.

Fault reads require nonseekable, record-aligned reads. They remove groups from the deliver list, allocate response cookies, compose one `iommu_hwpt_pgfault` per fault, copy to userspace, and restore the group if the buffer is too small or copy fails. Fault writes consume page-response records, validate response codes, erase matching cookies, respond to hardware, and free groups.

`iommufd_auto_response_faults()` is called on detach/replace to find pending groups for a dying attach handle in both deliver and response queues, respond invalid, and free them.

vEVENTQ allocation validates type/depth, locks the vIOMMU event queue list for write, rejects duplicate types, allocates an event queue object, references the vIOMMU, installs it on the vIOMMU list, initializes a lost-events header, creates an anon inode, finalizes the object, and installs the fd.

vEVENTQ reads fetch queued events. For lost-events headers it copies a temporary header so the permanent lost header can be reinserted when needed. Normal events decrement `num_events` after successful copy and are freed.

Poll reports `EPOLLOUT` for fault queues and `EPOLLIN|EPOLLRDNORM` when the deliver list is nonempty. Release drops the eventq object user ref and context ref.

## State And Persistence
State is in event queue objects, anon file references, wait queues, spinlock-protected deliver lists, fault response xarrays, vEVENTQ depths and event counters, and vIOMMU queue lists. No data persists after object/fd destruction.

## Dependencies And Integration Points
This file integrates with IOMMUFD object management, `iopf_group` hardware fault infrastructure, attach handles from IOMMU core/IOMMUFD, anon inodes, file descriptor installation, userspace UAPI records, polling, vIOMMU driver callbacks, and `driver.c` event reporting.

## Risks
Fault delivery is sensitive to cookie lifetime and attach-handle lifetime. If a detach path misses a pending group, userspace could respond to a stale hardware context; if it frees too early, readers can fault.

Record-size validation is strict; userspace must use exact multiples for fault records and responses. Partial copy handling must restore queues without losing groups.

vEVENTQ overflow behavior intentionally collapses events into a lost-events marker. Queue users must treat that marker as lossy state and resynchronize.

Locking mixes mutexes, spinlocks, xarrays, and rwsems; order must prevent races between read/write, destroy, detach auto-response, and driver event reporting.

## Test Signals
Exercise fault fd allocation, polling, multi-fault group reads, too-small reads, invalid response codes, duplicate/late responses, detach auto-invalid responses from deliver and response queues, vEVENTQ duplicate type rejection, queue overflow lost-events markers, read buffer boundaries, fd release refcounts, and destroy while queues hold pending events.
