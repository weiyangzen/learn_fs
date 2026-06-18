# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv84_fence.c

## Purpose
This file implements the NV84+ fence backend using per-channel semaphore slots in a shared BO and GPU virtual mappings rather than the older DMA object approach.

## Important APIs, Types, and Functions
Public functions include `nv84_fence_context_new` and `nv84_fence_create`. Internal helpers emit and wait on 32-bit semaphore values, compute channel IDs, read/write fence slots, suspend/resume slot contents, and destroy contexts/private state.

## Control Flow
Creation allocates `nv84_fence_priv`, chooses VRAM if available or coherent GART fallback, allocates a BO sized at 16 bytes per channel, and installs uevent-capable fence callbacks. Context creation allocates `nv84_fence_chan`, initializes callbacks, seeds the sequence from the BO slot, maps the fence BO into the channel VMM under a mutex, and stores the VMA. Emit writes a release method to the current channel's slot. Sync writes an acquire operation against the previous channel's slot. Context deletion writes the final sequence, drops the VMA, and frees the context.

## State and Persistence Behavior
State includes the shared fence BO, per-channel 16-byte slots, per-context VMA references, current sequence values, a mutex protecting VMA creation/deletion, and optional suspend snapshot array.

## Dependencies and Integration Points
It depends on Nouveau VMM/VMA helpers, BO read/write/mapping, NV826F push methods, channel runlist/chid base, and generic fence infrastructure.

## Risks
System-memory fallback must be coherent or fence polling can lose updates. Channel ID slot computation must match runlist layout. Suspend snapshot allocation failure reports false and may prevent safe suspend. VMA lifetime must match channel context lifetime.

## Test Signals
Signals include fence signaling on VRAM and coherent GART fallback, cross-channel sync, suspend/resume slot preservation, runlist channel ID correctness, and context teardown under active fences.
