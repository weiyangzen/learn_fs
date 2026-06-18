# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.h

## Purpose
This header declares Nouveau's classic VMM and VMA structures and helper functions.

## Important APIs, Types, and Functions
It defines `struct nouveau_vma` with VMM pointer, refs, list link, address, mapped memory, and fence pointer. It defines `struct nouveau_vmm` with client, NVIF VMM, and SVMM pointers. It declares VMA find/new/del/map/unmap and VMM init/fini.

## Control Flow
The header has no executable flow; it describes the state contract used by `nouveau_vmm.c`, BO code, and fence code.

## State and Persistence Behavior
VMA state persists while a BO has a GPU VA in a client VMM. VMM state persists for the client lifetime and may own an SVM manager.

## Dependencies and Integration Points
It includes NVIF VMM declarations and forward-declares Nouveau BO and memory. It integrates with BO VMA lists, memory mapping, fence tracking, and SVM.

## Risks
Any layout changes affect container users and list management. Callers must preserve refcount discipline and avoid stale fence/mem pointers.

## Test Signals
Build coverage and BO/fence VMA allocation tests validate the header.
