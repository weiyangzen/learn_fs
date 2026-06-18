# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.h

## Purpose
Declares the public G450/G550 output hooks used by the matroxfb base driver. It provides real prototypes when `CONFIG_FB_MATROX_G` is enabled and no-op inline stubs otherwise.

## Important APIs, Types, and Functions
- `matroxfb_g450_connect(struct matrox_fb_info *minfo)` installs G450 secondary/DVI output handlers.
- `matroxfb_g450_shutdown(struct matrox_fb_info *minfo)` removes those handlers.

## Control Flow
Including code calls these functions unconditionally. The header hides configuration differences by compiling to no-ops when the G450 support object is not built.

## State and Persistence
The header holds no state. The real implementation mutates `struct matrox_fb_info` output state.

## Dependencies and Integration Points
Includes `matroxfb_base.h` for `struct matrox_fb_info`. It is consumed by Matrox core initialization and shutdown paths.

## Risks
The no-op stubs make missing `CONFIG_FB_MATROX_G` support silent. Call sites must not assume output registration happened unless device flags and build config allow it.

## Test Signals
Build coverage with and without `CONFIG_FB_MATROX_G` should confirm call sites compile. Runtime validation is whether G450 outputs appear only in the enabled configuration.
