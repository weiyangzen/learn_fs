# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.h

## Purpose
Declares the GuC Render C-state control API.

## Important APIs, Types, And Functions
Forward-declares `struct xe_guc` and `enum slpc_gucrc_mode`, then declares init, enable, and disable functions.

## Control Flow
Callers initialize once, enable RC during GuC/GT power setup, and disable it during teardown or when reclaiming host control.

## State And Persistence
No state is exposed by the header; firmware and GT idle state are controlled by the implementation.

## Dependencies And Integration Points
Used by GT/GuC power-management setup and teardown paths.

## Risks And Test Signals
The header has a very small surface. Compile coverage and runtime RC enable/disable paths validate it.
