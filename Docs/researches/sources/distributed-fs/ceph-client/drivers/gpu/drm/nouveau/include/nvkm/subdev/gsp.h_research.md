# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/gsp.h

## Purpose

This header defines the GPU System Processor subdevice, including firmware packages, boot memory, WPR/FB layout, shared command/message queues, RPC reply policy, RM object wrappers, registry state, interrupt routing, suspend/resume memory, and debugfs logging buffers.

## Important APIs, Types, and Functions

Important elements include `struct nvkm_gsp`, `struct nvkm_gsp_mem`, `struct nvkm_gsp_radix3`, `enum nvkm_gsp_rpc_reply_policy`, `struct nvkm_gsp_client`, `struct nvkm_gsp_device`, `struct nvkm_gsp_object`, `struct nvkm_gsp_event`, `nvkm_gsp_mem_ctor`, `nvkm_gsp_mem_dtor`, `nvkm_gsp_sg`, and `nvkm_gsp_sg_free`.

## Control Flow

GSP initialization allocates DMA memory and scatter-gather/radix3 page tables, loads booter/FMC/boot/RM firmware, describes framebuffer/WPR regions, starts Falcon/GSP firmware, then communicates through shared command and message queues. RPC callers choose nowait, no-sequence, receive, or poll reply handling. RM object wrappers mirror GSP-owned handles for display, FIFO, VMM, and other services.

## State and Persistence Behavior

State is extensive: firmware references, DMA buffers, WPR metadata, BIOS/heap/region layout, suspend-resume buffers, shared queue pointers/counters/sequences, running flag, internal clients/devices, interrupt mappings, BAR PDB addresses, GR topology, registry RPC data, and optional debugfs dentries. Most state persists while GSP-RM is running and must be rebuilt after full firmware reset.

## Dependencies and Integration Points

It depends on Falcon firmware loading, NVKM subdev lifecycle, Linux firmware/DMA/SG/debugfs APIs, RM generated headers, display/FIFO/MMU clients, and device interrupt routing.

## Risks

DMA buffer lifetime and alignment are critical because firmware dereferences these structures. RPC sequence policy mistakes can deadlock callers or drop replies. GSP/non-GSP paths must preserve the same high-level NVKM contracts despite different ownership of hardware programming.

## Test Signals

Validate GSP boot/unload, DMA/radix3 allocation cleanup, RPC timeout/reply policies, event notification delivery, debugfs log exposure, suspend/resume memory handoff, and fallback on firmware load failures.
