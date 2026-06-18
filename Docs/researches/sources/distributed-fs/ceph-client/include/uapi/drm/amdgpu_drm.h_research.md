# sources/distributed-fs/ceph-client/include/uapi/drm/amdgpu_drm.h

## Purpose
Defines the public AMDGPU DRM ioctl ABI for buffer management, virtual memory, command submission, synchronization, scheduling, user queues, metadata, and device information.

## Important APIs, Types, And Functions
Key exports include `DRM_IOCTL_AMDGPU_*`, GEM create/mmap/wait/userptr/op/list structs, BO list structs, context operations and reset state, user queue create/signal/wait/MQD metadata, VM reserve and VA map/unmap structures, scheduler priority override, CS chunk structures, fence/syncobj conversion, tiling helpers, info query IDs, memory/device/HW IP/video/VBIOS/GPUVM fault structs, VRAM type constants, and GPU family constants.

## Control Flow
The header contains no executable control flow, but it encodes ioctl workflows: create GEM, map VA, create context or user queue, submit CS chunks with fences and dependencies, wait or convert fences, query device state, and update metadata. Unions split in/out payloads for bidirectional ioctls.

## State, Persistence, And Dependencies
Kernel state addressed by this ABI includes GEM BOs, BO lists, GPU VMs, contexts, scheduler priority overrides, syncobjs, fences, user queues, doorbells, and device telemetry. It depends on `drm.h`.

## Integration Points
Used by Mesa/RADV/RadeonSI, ROCm components, libdrm_amdgpu, window systems, compute runtimes, kernel AMDGPU ioctl handlers, TTM memory management, DRM syncobj, PRIME/GEM, and firmware discovery paths.

## Risks
Every ioctl number, flag, and struct layout is ABI. User pointers and counts require validation. Userptr is explicitly unreliable and needs fallbacks. VM mapping flags interact with cache coherence, encryption, DCC, and PTE memory types. High-priority queues and secure queues require authorization.

## Test Signals
libdrm_amdgpu ioctl tests, Mesa/ROCm conformance, GEM create/map/free stress, CS submission and fence waits, VM bind/unbind fault tests, 32/64-bit struct checks, userptr fallback tests, syncobj timeline tests, GPU reset/RAS query tests, and info query compatibility tests.
