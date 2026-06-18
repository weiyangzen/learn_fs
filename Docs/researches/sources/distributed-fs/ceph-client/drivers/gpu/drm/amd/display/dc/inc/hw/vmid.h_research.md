# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vmid.h

## Purpose

`vmid.h` defines the VMID hardware abstraction for display virtual memory contexts. It lets DC set page-table base/range and invalidate or manage VMID state used by GPU virtual-address scanout paths.

## Important APIs, Types, And Functions

The file defines `struct vmid` with context, instance, and `vmid_funcs`. The vtable exposes VMID setup and invalidation style operations for page-table address/range programming and hardware synchronization, implemented by ASIC-specific VM helpers.

## Control Flow

When a plane uses GPU virtual addressing, resource or VM helper code programs a VMID with page-table information before scanout. Updates must occur before the hubp/memory input consumes the virtual address, and invalidation must be coordinated with page-table changes.

## State And Persistence Behavior

VMID state persists in hardware VM registers and affects address translation for display fetches. Software object state is only context/instance/vtable.

## Dependencies And Integration Points

The header integrates with `vm_helper.h`, resource pools, GPUVM/page-table code, and HUBP/memory input programming. It is part of the path that keeps display scanout coherent with memory-management state.

## Risks And Test Signals

Risks include stale page tables, wrong VMID assignment, missing invalidation, and scanout faults. Test signals include GPUVM-backed framebuffer scanout, page-table updates during flips, virtual-address fault logs, multi-plane VMID use, and suspend/resume with active framebuffers.
