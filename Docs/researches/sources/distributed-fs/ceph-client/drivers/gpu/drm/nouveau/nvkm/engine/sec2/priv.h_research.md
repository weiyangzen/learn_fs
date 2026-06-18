# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/priv.h

## Purpose
Defines SEC2 private function contracts shared by SEC2 generation files and the common core.

## Important APIs, types, and functions
`struct nvkm_sec2_func` describes falcon ops, firmware unit ids, optional interrupt vector lookup, interrupt handler, and init-message parser. `struct nvkm_sec2_fwif` maps firmware versions to load routines, runtime functions, and ACR low-secure functions. It declares constructors and shared GP102 helpers including ACR bootloader write/patch callbacks.

## Control flow, state, and persistence
No runtime code exists. The structs determine how `nvkm_sec2_new_()` chooses firmware, builds a falcon, registers interrupts, sends unload commands, and exposes ACR integration.

## Dependencies and integration points
Includes public `engine/sec2.h` and forward declares ACR low-secure firmware. Used by all SEC2 implementation files and R535 alternate construction.

## Risks and test signals
Signature drift breaks all SEC2 generations at build time. Mis-set unit ids or callback pointers surface as init-message failures, unload failures, or ACR bootstrap errors.
