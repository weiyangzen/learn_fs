# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.h

## Purpose
Declares the optional GK20A devfreq interface and stubs it out when `CONFIG_PM_DEVFREQ` is disabled.

## Important APIs, types, and functions
Forward declares `struct gk20a_devfreq`; declares `gk20a_devfreq_init()`, `gk20a_devfreq_resume()`, and `gk20a_devfreq_suspend()` for devfreq builds, and provides inline no-op fallbacks otherwise.

## Control flow
No complex flow exists. Configuration decides whether callers get real devfreq functions or no-op inline helpers returning success.

## State and persistence
No state is defined beyond the opaque devfreq pointer type. Real state lives in `gk20a_devfreq.c`.

## Dependencies and integration points
Includes Linux devfreq declarations and is used by GK20A, GM20B, and GP10B clock implementations to avoid conditional code in init/resume paths.

## Risks
The disabled-config stub for init leaves the caller's devfreq pointer untouched; callers must not dereference it unless the real init has populated it.

## Test signals
Build both with and without `CONFIG_PM_DEVFREQ`; runtime no-op suspend/resume should succeed when devfreq is absent.
