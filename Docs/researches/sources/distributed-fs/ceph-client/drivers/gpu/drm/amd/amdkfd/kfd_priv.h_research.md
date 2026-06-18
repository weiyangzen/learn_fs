
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_priv.h

## Purpose
Central private KFD header declaring process, device, queue, packet-manager, CRIU, doorbell, event, topology, interrupt, SVM, and debugfs contracts shared across the AMD KFD driver.

## Important APIs, types, and functions
- Core device types: `struct kfd_dev`, `struct kfd_node`, `struct kfd_device_info`, `struct kfd_mem_obj`.
- Queue types: `struct queue_properties`, `struct queue`, `struct process_queue_manager`, `struct qcm_process_device`, `struct process_queue_node`.
- Process types: `struct kfd_process_device`, `struct svm_range_list`, `struct kfd_process`.
- CRIU structs: process, device, BO, queue, event, and SVM private data.
- Packet-manager contracts: `struct packet_manager`, `struct packet_manager_funcs`, PM send APIs, and PM4 header helper.
- Function prototypes cover process lifecycle, queue management, MQD managers, DQM, kernel queues, doorbells, events, topology, interrupts, CWSR, and debugfs.

## Control flow
The header has inline helpers only. `kfd_flush_tlb` calls the amdgpu VM TLB flush for a PDD. `kfd_flush_tlb_after_unmap`, `kfd_devcgroup_check_permission`, `kfd_is_first_node`, `kfd_node_by_irq_ids`, and small GPU-ID/PDD lookup helpers encode common policy.

## State and persistence behavior
This file defines the persistent in-kernel state layout for KFD processes and queues: queue BO references, MQD pointers, PDD IDRs, doorbell bitmaps, eviction fences/work items, sysfs kobjects, SVM ranges, debug trap state, CRIU private data, and per-process context IDs. It also defines user-visible CRIU private structure versioning.

## Dependencies and integration points
Pulls in Linux MMU notifier, workqueue, mutex, spinlock, IDR, sysfs, DRM, amdgpu, kgd-kfd interface, and KFD UAPI headers. Nearly every file in this group depends on these definitions.

## Risks
Because this is the shared internal ABI, field ownership and locking comments are critical. Queue active/evicted/suspended/GWS state is DQM-lock protected but exposed through multiple call paths. CRIU private structure changes require `KFD_CRIU_PRIV_VERSION` updates. Doorbell and mmap offset bit encodings are user-visible. Inline permission and IRQ node matching must handle partitioned/multi-AID devices correctly.

## Test signals
Full KFD build coverage, queue lifecycle tests, CRIU checkpoint/restore compatibility tests, SVM page-fault tests, debug trap attach/detach, sysfs/procfs visibility, doorbell mmap, device-cgroup permission tests, and suspend/resume eviction tests.
