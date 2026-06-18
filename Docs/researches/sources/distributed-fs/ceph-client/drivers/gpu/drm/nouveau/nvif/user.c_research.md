# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/user.c

## Purpose
This file constructs and destroys NVIF usermode objects used for fast device time reads and doorbell submission on newer GPUs.

## Important APIs, Types, and Functions
Public functions are `nvif_user_ctor` and `nvif_user_dtor`.

## Control Flow
Constructor returns early if usermode is already available, selects a supported usermode class from Blackwell through Volta, creates the object, maps it, and stores the class function table. Destructor destroys the usermode object and clears the function pointer if present.

## State and Persistence Behavior
State persists in `device->user.object`, mapped object memory, and `device->user.func`.

## Dependencies and Integration Points
It depends on NVIF object class selection, usermode class IDs, object mapping, and `nvif_userc361` function implementation. Channel C36F code uses doorbells from this interface.

## Risks
The return value from `nvif_object_map` is ignored, so a function table can be installed even if mapping failed. Unsupported classes return the class-selection error.

## Test Signals
Signals include usermode construction on Volta+ GPUs, mapping failure injection, device time via usermode, C36F doorbell submission, and destructor cleanup.
