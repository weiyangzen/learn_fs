# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/parent.h

## Purpose
Defines the NVIF parent logging callback interface shared by child objects.

## Important APIs, Types, And Functions
Defines `struct nvif_parent`, `struct nvif_parent_func` with `debugf` and `errorf`, plus inline constructor/destructor.

## Control Flow
Construction stores the function table; destruction clears it. Logging macros later call through the parent function table.

## State And Persistence
The function-table pointer persists while the parent object is alive.

## Dependencies And Integration Points
Used by `nvif/printf.h` and embedded in parent-capable NVIF objects.

## Risks
Logging through a cleared or stale parent function pointer can crash. Teardown order must prevent child logging after parent destruction.

## Test Signals
Debug/error logging during object lifecycle and teardown race tests validate behavior.
