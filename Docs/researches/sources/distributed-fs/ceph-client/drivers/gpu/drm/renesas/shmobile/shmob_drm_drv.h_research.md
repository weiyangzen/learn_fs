# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h

## Purpose

`shmob_drm_drv.h` defines the top-level private state for the legacy SH Mobile DRM driver.

## Important APIs, Types, and Functions

`struct shmob_drm_config` stores clock source and divider. `struct shmob_drm_device` stores Linux device, optional platform data, copied config, MMIO, clock, `lddckr`, IRQ number/lock, DRM device, CRTC, encoder, and connector. `to_shmob_device()` converts from `drm_device`.

## Control Flow

Probe initializes this structure; CRTC/KMS/IRQ/PM code read and mutate it throughout device lifetime.

## State and Persistence Behavior

The structure persists as the managed DRM private object. `irq_lock` protects `LDINTR` register access, while runtime PM controls the clock.

## Dependencies and Integration Points

It depends on Linux platform-data definitions, spinlocks, and local CRTC declarations.

## Risks and Edge Cases

The structure mixes OF-derived config and legacy platform data; code must check `pdata` before using fixed-panel fields. IRQ lock usage must remain consistent.

## Test Signals

OF and platform-data probe coverage plus lockdep under IRQ/vblank paths validate this header.
