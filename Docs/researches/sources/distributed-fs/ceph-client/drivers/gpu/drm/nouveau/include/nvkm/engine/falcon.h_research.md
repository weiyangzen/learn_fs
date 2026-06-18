# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/falcon.h

## Purpose

This header defines `struct nvkm_falcon`, the engine-facing representation of Falcon microcontrollers. It captures register bases, firmware code/data windows, ownership locking, DMA index constants, and chip-specific function tables.

## Important APIs, Types, and Functions

Important elements are `enum nvkm_falcon_dmaidx`, `struct nvkm_falcon`, `struct nvkm_falcon_func`, `nvkm_falcon_get`, `nvkm_falcon_put`, `nvkm_falcon_new_`, `nvkm_falcon_rd32`, `nvkm_falcon_wr32`, `nvkm_falcon_mask`, `nvkm_falcon_load_imem`, `nvkm_falcon_load_dmem`, and `nvkm_falcon_start`.

## Control Flow

An engine constructor embeds a Falcon, fills generation-specific function pointers, then users acquire it through `nvkm_falcon_get` before reset, load, start, or queue operations. Register helpers offset all accesses by the Falcon base address. Optional function pointers select/reset RISC-V variants, bind instance memory, configure PIO/DMA loaders, dispatch interrupts, and publish user object classes.

## State and Persistence Behavior

State includes owner/user subdevices, mutexes, one-time init flag, version/security/debug bits, optional core memory, code/data blob metadata, external ownership, and the embedded `nvkm_engine`. Hardware state persists in Falcon registers and loaded microcode until reset.

## Dependencies and Integration Points

It is included by the core Falcon loader, PMU/SEC2/GSP/video engines, and chip-specific Falcon implementations. It depends on `core/engine.h`, NVKM device MMIO helpers, and channel-aware interrupt callbacks.

## Risks

Ownership errors can allow concurrent firmware access. Wrong DMA index or register base corrupts unrelated engine state. RISC-V Falcon reset/interrupt paths must not be treated as classic Falcon behavior.

## Test Signals

Test Falcon acquire/release locking, IMEM/DMEM load on engines using static blobs and runtime firmware, start/reset sequencing, interrupt dispatch, and suspend/resume reinitialization.
