# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/Kbuild

## Purpose
This Kbuild fragment includes the NVKM subtrees that make up Nouveau's kernel-mode hardware backend.

## Important APIs, Types, and Functions
It includes Kbuild fragments for `core`, `nvfw`, `falcon`, `subdev`, and `engine`.

## Control Flow
There is no runtime flow. The build system expands these included fragments to populate NVKM object lists.

## State and Persistence Behavior
No runtime state exists. Build state is the set of included subdirectories.

## Dependencies and Integration Points
It is included by Nouveau's parent Kbuild and aggregates NVKM backend source selection.

## Risks
Missing or misordered includes can omit whole backend classes or break object list definitions.

## Test Signals
Kernel build and link coverage validate this file.
