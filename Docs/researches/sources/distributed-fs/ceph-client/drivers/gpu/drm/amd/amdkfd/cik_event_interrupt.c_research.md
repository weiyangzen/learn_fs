# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_event_interrupt.c

## Purpose
`cik_event_interrupt.c` implements KFD event interrupt filtering and workqueue processing for CIK-era GPUs. It converts selected IH ring entries into user-visible KFD events, hardware-exception events, SMI VM fault notifications, and process-device eviction on VM faults.

## Important APIs, Types, And Functions
The file exports `event_interrupt_class_cik`, a `struct kfd_event_interrupt_class` with `.interrupt_isr = cik_event_interrupt_isr` and `.interrupt_wq = cik_event_interrupt_wq`. The ISR parses `struct cik_ih_ring_entry`, filters KFD VMID ranges, validates PASID, handles a Hawaii VM fault workaround, and selects interrupt source IDs. The workqueue handler signals events via `kfd_signal_event_interrupt()`, `kfd_signal_hw_exception_event()`, `kfd_signal_vm_fault_event()`, and calls `kfd_evict_process_device()`.

## Control Flow
The interrupt top half receives an IH entry and either rejects it or marks it for deferred KFD processing. For Hawaii VM faults, it patches missing VMID/PASID information by reading VM fault registers and ATC VMID/PASID mappings through `kfd2kgd` callbacks. Normal entries extract VMID/PASID from `ring_id`, reject non-KFD VMIDs and zero PASIDs, and accept EOP, SDMA trap, SQ message, bad opcode, and optionally VM fault sources. The workqueue then decodes the same source IDs and signals the appropriate event or fault path.

## State And Persistence
This file does not own persistent structures, but it mutates event state in KFD process/event subsystems, updates SMI VM fault state, evicts process-device queues on faults, and may write a patched IH entry into caller-provided storage. It also references global module policy `amdgpu_no_queue_eviction_on_vm_fault`.

## Dependencies And Integration Points
It depends on `kfd_priv.h`, `kfd_events.h`, `cik_int.h`, `amdgpu_amdkfd.h`, `kfd_smi_events.h`, KFD VMID range metadata, and KGD callbacks in `struct kfd2kgd_calls`. `kfd_device.c` installs `event_interrupt_class_cik` for CIK devices.

## Risks
Interrupt filtering must be exact: accepting foreign VMIDs could signal the wrong process, while rejecting valid PASIDs can lose user events or faults. The Hawaii workaround trusts fallback register reads and mapping callbacks. VM fault handling must unref looked-up processes on all paths; this file does so after signaling or after empty fault info, but early `!pdd` returns rely on lookup semantics. Queue eviction policy is tied to `amdgpu_no_queue_eviction_on_vm_fault`.

## Test Signals
Signals include EOP, SDMA trap, and SQ message user event delivery; bad opcode hardware exception delivery; CIK VM fault reporting with process eviction; Hawaii-specific patched VM fault entries; no warnings for valid PASIDs; and interrupt rejection for non-KFD VMIDs. Stress tests should include concurrent process teardown during fault handling.
