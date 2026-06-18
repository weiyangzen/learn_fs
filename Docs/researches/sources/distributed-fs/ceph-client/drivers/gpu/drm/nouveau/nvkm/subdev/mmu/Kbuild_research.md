# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/Kbuild

## Purpose
Builds the Nouveau NVKM MMU core, chip-specific MMU descriptors, memory object implementations, VMM backends, and user object wrappers.

## Important APIs, Types, and Functions
The build list covers `base.o`, chip MMU files from NV04 through GH100, memory implementations `mem*.o`, VMM implementations `vmm*.o`, and user ABI wrappers `umem.o`, `ummu.o`, `uvmm.o`.

## Control Flow, State, and Persistence
No runtime flow exists. The object list determines available MMU constructors, VMM page-table layouts, and user-space NVIF classes.

## Dependencies and Integration Points
Integrated by parent NVKM Kbuild and must match constructor references in device tables and symbols declared in `mem.h`, `vmm.h`, and `priv.h`.

## Risks and Test Signals
Missing entries cause unresolved symbols or disabled GPU families. Signals include full Nouveau kernel builds, module load, user memory allocation, and VMM creation on each generation.
