# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/user.h

## Purpose
Declares the NVIF usermode object wrapper for doorbell and time access.

## Important APIs, Types, And Functions
Defines `struct nvif_user`, `struct nvif_user_func` with `doorbell` and `time`, `nvif_user_ctor/dtor`, and external `nvif_userc361` function table.

## Control Flow
Construction creates a usermode object under the device. Function callbacks ring a doorbell or read GPU time.

## State And Persistence
User object state stores function table and embedded object while the device/usermode interface exists.

## Dependencies And Integration Points
Depends on `nvif/object.h`; used by `nvif_device`, channel doorbell submission, and timer paths.

## Risks
Doorbell token misuse can notify the wrong channel. Function table must match the usermode class generation.

## Test Signals
Usermode object creation, channel doorbell kicks, GPU time reads, and teardown validate behavior.
