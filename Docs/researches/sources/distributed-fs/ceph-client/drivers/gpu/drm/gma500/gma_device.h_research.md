<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h

## Purpose

This header declares the shared GMA core-frequency helper.

## Important APIs, Types, And Functions

It forward-declares `struct drm_device` and declares `gma_get_core_freq(struct drm_device *dev)`.

## Control Flow

No executable flow exists. Chip setup files call the declared helper during device initialization.

## State And Persistence

No state is stored here. The helper mutates `drm_psb_private.core_freq`.

## Dependencies And Integration Points

It provides a small interface between chip-specific setup files and `gma_device.c`.

## Risks And Test Signals

Risks are declaration drift and missing include guards in consumers. Test signals are build/link success and chip setup storing a nonzero core frequency on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h -->
