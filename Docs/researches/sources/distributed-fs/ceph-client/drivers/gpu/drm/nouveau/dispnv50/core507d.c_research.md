<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c

## Purpose
This file implements the NV507D display core channel and shared core helpers for notifier setup, capability reads, updates, initialization, and construction.

## Important APIs, Types, and Functions
It defines `core507d_update`, `core507d_ntfy_wait_done`, `core507d_ntfy_init`, `core507d_read_caps`, `core507d_caps_init`, `core507d_init`, `core507d_new_`, and `core507d_new`, plus the `core507d` function table.

## Control Flow
Update optionally enables a write notifier, emits an UPDATE method with base and overlay interlock flags plus interrupt/driver-friendly bits, disables notify, and kicks the push buffer. Capability init clears the caps notifier, sends `GET_CAPABILITIES`, then waits up to two seconds for the notifier done bit. Init sets the context DMA notifier. Constructor allocates `struct nv50_core`, assigns the function table/display pointer, and creates the display DMA channel using the shared sync BO.

## State and Persistence Behavior
The file initializes notifier memory in the sync BO, programs persistent core channel context DMA, and uses push-buffer methods to update hardware state. The function table references head/output implementations for NV507D-era hardware.

## Dependencies and Integration Points
It depends on NVIF push/timer, class `cl507d`, BO notifier macros, `nv50_dmac_create`, `nv50_disp` sync layout, and head/output function tables `head507d`, `dac507d`, `sor507d`, and `pior507d`.

## Risks
Notifier and caps waits can time out, but caps init returns success after logging timeout. Update interlock flags must match pending plane/core changes or commits can tear. Constructor error paths can leave allocated core memory for caller cleanup.

## Test Signals
Core channel allocation, init notifier DMA, atomic commits with and without notify, caps reads, notifier timeout injection, output control on DAC/SOR/PIOR, and suspend/unload channel destruction are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c -->
