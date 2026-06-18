# sources/control-plane/ceph-csi/internal/rbd/diskusage.go

## Purpose
Adds disk-space reclamation support for RBD images through `rbdImage.Sparsify`, used by CSI-Addons reclaim-space workflows to punch out zero-filled extents and reduce backend usage.

## Important APIs, Types, And Functions
`(*rbdImage).Sparsify(ctx)` checks whether the image is in use, opens the image, reads image order from `Stat`, and calls go-ceph/librbd `Sparsify` with an object-size granularity of `1 << imageInfo.Order`. It returns `rbderrors.ErrImageInUse` when active I/O is detected.

## Control Flow
The function first calls `isInUse`; any check failure is wrapped. If the image is active, it refuses to sparsify. Otherwise it opens the image, defers close with warning logging on close failure, fetches image stats, and invokes librbd sparsification.

## State And Persistence
The operation mutates backend RBD allocation state by freeing zeroed blocks. It does not alter CSI journals or image metadata. The only local state is the temporary opened librbd image handle.

## Dependencies And Integration Points
Depends on `rbdImage` open/in-use helpers, go-ceph librbd image methods, package errors, and logging. The method is part of the broader RBD image abstraction consumed by CSI-Addons reclaim-space servers registered in the driver.

## Risks And Test Signals
Main risks are running against an image that is actively used despite `isInUse` checks, choosing a granularity inappropriate for some image layouts, and propagation of low-level librbd failures. This file has no direct unit test in the subset; meaningful coverage likely requires integration tests against a real image.
