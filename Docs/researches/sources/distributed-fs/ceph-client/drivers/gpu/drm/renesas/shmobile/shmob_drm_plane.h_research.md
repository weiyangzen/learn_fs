# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.h

## Purpose
Declares the SH Mobile DRM plane creation interface used by the broader shmobile KMS setup.

## Important APIs, Types, And Functions
Forward declares `struct drm_plane` and `struct shmob_drm_device`, then exports `shmob_drm_plane_create(struct shmob_drm_device *sdev, enum drm_plane_type type, unsigned int index)`.

## Control Flow
This header has no runtime control flow. It provides the constructor contract for code that needs to instantiate primary or overlay planes.

## State And Persistence
No state is stored here. State ownership lives in the implementation file and DRM plane core.

## Dependencies And Integration Points
The prototype depends on DRM's `enum drm_plane_type` being visible to includers. It connects shmobile KMS initialization with the plane implementation.

## Risks
The header does not include a DRM header for `enum drm_plane_type`; includers must already have a suitable DRM declaration. Misordered includes could expose compile failures.

## Test Signals
Build coverage is the primary signal. A successful shmobile KMS build and plane creation path validates this contract.
