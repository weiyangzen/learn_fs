# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/vm_helper.h

## Purpose

`vm_helper.h` declares helper APIs for display virtual-memory setup. It provides a small common layer for mapping DC state to VMID programming and page-table related hardware setup.

## Important APIs, Types, And Functions

The header declares VM helper routines that operate on DC objects, VMID hardware objects, and address/page-table parameters. These helpers coordinate VMID use for display scanout and abstract ASIC-specific details behind VMID or resource interfaces.

## Control Flow

When virtual-addressed surfaces are used, display setup prepares VM information, programs VMID state through helper calls, and ensures hardware translation is valid before memory fetch begins. Invalidation and reset paths coordinate with modeset or page-table changes.

## State And Persistence Behavior

The header stores no state. Persistent behavior is hardware VMID/page-table configuration and any associated DC resource state tracking which VMID belongs to which pipe or surface.

## Dependencies And Integration Points

It integrates with `vmid.h`, resource mapping, GPU memory management, HUBP/memory input programming, and page-flip paths for virtual-address framebuffers.

## Risks And Test Signals

Risks include programming order bugs, stale page-table bases, missing invalidation, and address translation faults during scanout. Test signals include GPUVM framebuffers, page flips under memory pressure, VM fault logs, multi-plane virtual scanout, and resume after VRAM/page-table changes.
