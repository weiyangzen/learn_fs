<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h

## Purpose
Defines the central Lima device model, GPU/IP/pipe IDs, IP block representation, device-wide state, polling helper, and device lifecycle prototypes.

## Important APIs, types, and functions
Enums define Mali400/Mali450 IDs, all IP blocks, and GP/PP pipe IDs. `struct lima_ip` wraps an IP block's device, id, presence, MMIO, IRQ, and per-IP union state. `struct lima_device` stores platform, DRM, clocks, reset, regulator, IPs, scheduler pipes, VM bounds, DLBU page, devfreq, and error-dump state. `to_lima_dev()` and `lima_poll_timeout()` are important helpers.

## Control flow
`lima_poll_timeout()` repeatedly calls a supplied poll function until success or timeout, sleeping between attempts when requested. Other content is declarative.

## State and persistence
The structures describe the full runtime state for one Lima GPU and its IP blocks. This state persists for the platform device lifetime.

## Dependencies and integration points
Includes DRM device, Linux list/mutex/delay, scheduler, dump, and devfreq headers. Used by nearly every Lima source file.

## Risks
The central header couples many modules; structure changes are high blast radius. The polling helper returns success immediately on a truthy callback and assumes callers provide safe timeout values.

## Test signals
Build coverage across all Lima files and runtime probe/suspend/job tests validate these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_device.h -->
