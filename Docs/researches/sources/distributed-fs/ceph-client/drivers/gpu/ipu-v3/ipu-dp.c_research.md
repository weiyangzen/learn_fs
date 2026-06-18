# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dp.c

## Purpose
Implements the IPUv3 Display Processor layer for foreground/background composition, global alpha, color-space conversion, foreground positioning, and flow/channel enablement.

## Important APIs, Types, and Functions
`struct ipu_dp`, `struct ipu_flow`, and `struct ipu_dp_priv` model DP channels, sync/async flows, and global state protected by a mutex. Exported APIs include `ipu_dp_set_global_alpha()`, `ipu_dp_set_window_pos()`, `ipu_dp_setup_channel()`, `ipu_dp_enable()/disable()`, `ipu_dp_enable_channel()/disable_channel()`, `ipu_dp_get()/put()`, and init/exit. `ipu_dp_csc_init()` writes hard-coded CSC matrices for RGB/YUV conversion combinations.

## Control Flow
Initialization maps the DP register page and creates three flows: sync, async0, and async1. Clients acquire a DP channel by flow, configure input/output color spaces and foreground/background behavior, optionally set alpha/window position, then enable the global DP module and the specific channel. Disable clears channel enable, foreground enable, and foreground position; sync disable can request SRM DP update through common code.

## State and Persistence
State is DP flow/channel in-use flags and hardware registers for composition, CSC, alpha, and positions. The mutex serializes register updates and allocation. No filesystem persistence exists.

## Dependencies and Integration Points
Depends on DRM color management definitions for color-space concepts, IPU color-space helpers, and common module enable/SRM update functions. It integrates with DMFC/DC/DI display output and display clients that compose overlay/primary planes.

## Risks
CSC coefficients are fixed tables; unsupported or mismatched color spaces can produce wrong colors. Foreground/background configuration depends on caller channel roles. `ipu_dp_disable_channel()` optionally syncs through SRM, so callers must choose the correct sync behavior for active display updates. Shared flow state requires balanced get/put.

## Test Signals
Plane composition tests with global alpha on/off, foreground position changes, RGB-to-YUV and YUV-to-RGB output validation, async/sync flow coverage, and modeset enable/disable stress are key. Visual color bars and CRCs can detect CSC regressions.
