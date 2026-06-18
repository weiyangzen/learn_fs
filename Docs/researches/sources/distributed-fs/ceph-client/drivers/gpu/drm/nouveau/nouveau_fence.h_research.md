
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.h

## Purpose
Declares Nouveau's fence objects, per-channel fence context, fence backend operations, common fence APIs, and hardware-generation fence constructor prototypes.

## Important APIs, Types, and Functions
`struct nouveau_fence` embeds a `dma_fence`, pending-list node, RCU channel pointer, and timeout. `struct nouveau_fence_chan` stores pending/flip lists, backend callbacks (`emit`, `sync`, `read`, `emit32`, `sync32`), sequence/context IDs, event work, NVIF event, and lifetime flags. `struct nouveau_fence_priv` describes the per-device fence backend with destructor, suspend/resume, context creation/destruction, and uevent capability. The header declares common fence operations and backend constructors for NV04, NV10, NV17, NV50, NV84, NVC0, and GV100 paths.

## Control Flow
Callers create or emit fences through the common APIs without knowing the backend generation. Channel initialization installs a `nouveau_fence_chan`, and acceleration setup selects the right backend based on channel class. Backend callbacks supply the hardware-specific sequence write/read/sync behavior.

## State and Persistence
The header defines persistent channel fence context and per-device fence backend state. NV84-specific extensions add a BO, suspend buffer, and mutex for fence storage.

## Dependencies and Integration Points
Depends on Linux `dma-fence` and NVIF events. It is included by the core driver header and therefore by GEM, EXEC, DMEM, channel, display, and BO code.

## Risks and Test Signals
Any structure layout or callback contract changes affect multiple GPU generations. Tests should cover backend selection, suspend/resume per fence generation, channel context allocation/free, fence wait/signal under interrupt and polling modes, and build coverage across old and new hardware support.
