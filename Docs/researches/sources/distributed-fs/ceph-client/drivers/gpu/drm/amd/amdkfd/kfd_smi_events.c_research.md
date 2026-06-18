# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.c

## Purpose
Implements the KFD SMI event stream exported through an anonymous file descriptor. User space opens the stream through `kfd_smi_event_open`, writes an event mask, then polls and reads textual SMI records for GPU reset, thermal throttling, VM faults, SVM page faults, migrations, queue eviction/restore, GPU unmap, and process start/end.

## Important APIs, Types, And Functions
`struct kfd_smi_client` is the per-open state: RCU list node, `kfifo`, wait queue, enabled event bitmask, target `kfd_node`, spinlock, opener pid, and `CAP_SYS_ADMIN` status. `kfd_smi_ev_fops` wires `poll`, `read`, `write`, and `release` to the anonymous inode. `kfd_smi_ev_write` updates the 64-bit event mask with `WRITE_ONCE`; `kfd_smi_ev_read` drains bytes from the FIFO under spinlock and copies them to user memory after unlocking. `kfd_smi_event_add` formats records using KFD SMI event format macros and dispatches through `add_event_to_kfifo`. The exported `kfd_smi_event_*` helpers convert KFD, SVM, VM, reset, and queue lifecycle events into SMI records.

## Control Flow
`kfd_smi_event_open` allocates a client, allocates an 8192-byte FIFO, records `current->tgid` and admin status, links the client into `dev->smi_clients` under `dev->smi_lock`, and returns an anonymous fd. Producers call event helpers, which format into a fixed `KFD_SMI_EVENT_MSG_SIZE` buffer, then walk `dev->smi_clients` under RCU. `kfd_smi_ev_enabled` allows per-pid events only for the owning pid unless the client is privileged. Matching clients receive FIFO bytes under their client spinlock and waiters are woken. `release` removes the client with `list_del_rcu` and frees it via `call_rcu`.

## State And Persistence
State is in-memory and per open fd. Event masks persist until userspace writes a new mask or closes the fd. FIFO contents are transient and dropped if there is insufficient FIFO space. `dev->reset_seq_num` is incremented on pre-reset events and included in both pre/post reset messages.

## Dependencies And Integration Points
Uses Linux `anon_inode_getfd`, `poll_wait`, `kfifo`, RCU, wait queues, and user copy helpers. Integrates with `amdgpu_vm_get_task_info_pasid`, `amdgpu_vm_get_task_info_vm`, `amdgpu_reset_get_desc`, `amdgpu_dpm_get_thermal_throttling_counter`, KFD process lookup, and SVM event producers. The header exposes these helpers to reset, VM fault, queue, and SVM code paths.

## Risks
Events can be silently lost when a client FIFO lacks space. `kfd_smi_event_add` relies on bounded formatting into a fixed buffer; format macro changes need size scrutiny. `kfd_smi_ev_read` returns `-EAGAIN` for empty streams, so blocking behavior depends on userspace using poll/select correctly. Authorization is pid based unless the opener had `CAP_SYS_ADMIN`; incorrect pid selection in producers can leak or suppress process-scoped events. RCU removal and FIFO access rely on consistent use of `dev->smi_lock` and per-client spinlocks.

## Test Signals
Useful tests include opening SMI events, writing individual masks, verifying poll readiness after injected reset/fault/migration events, reading partial and full FIFO records, closing while events are produced, validating non-admin pid filtering, validating admin sees cross-process events, and stress tests that intentionally overflow the FIFO and confirm debug-only drops without memory corruption.
