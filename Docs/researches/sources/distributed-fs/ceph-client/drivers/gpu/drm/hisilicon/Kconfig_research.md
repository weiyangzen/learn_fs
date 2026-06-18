
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Kconfig

## Purpose
`hisilicon/Kconfig` is the top-level Kconfig include file for Hisilicon DRM drivers.

## Important APIs, Types, And Functions
It sources `drivers/gpu/drm/hisilicon/hibmc/Kconfig` and `drivers/gpu/drm/hisilicon/kirin/Kconfig`, with a comment requesting alphabetical ordering.

## Control Flow
There is no runtime flow. During kernel configuration, this file makes the HIBMC and Kirin DRM driver options visible under the Hisilicon DRM subtree.

## State And Persistence
The file stores build-time menu inclusion state only.

## Dependencies And Integration Points
It integrates with the DRM Kconfig hierarchy and delegates concrete options to child Kconfig files. In this work item, the relevant child is `hibmc/Kconfig`.

## Risks
Incorrect source paths or ordering mistakes can hide driver options from configuration. Adding new Hisilicon drivers requires updating this file.

## Test Signals
Kconfig tests should confirm `DRM_HISI_HIBMC` and Kirin options appear when the parent DRM menu is parsed and that all sourced paths exist.
