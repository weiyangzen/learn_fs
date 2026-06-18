# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.h

## Purpose

`malidp_drv.h` is the internal driver-state header for the ARM Mali-DP DRM driver. It defines the DRM-private object, plane and CRTC extension state, config-valid constants, debug error statistics, helper conversion macros, and local cross-file function declarations.

## Important APIs, Types, And Functions

`struct malidp_drm` embeds `struct drm_device` and stores the hardware device pointer, CRTC, writeback connector, config-valid waitqueue/atomic, pending vblank event, core ID, and debug error stats. `struct malidp_plane` extends `struct drm_plane` with hardware layer metadata. `struct malidp_plane_state` records rotation-memory need, internal format ID, plane count, and MMU prefetch choice. `struct malidp_crtc_state` stores gamma/color-adjust coefficients, scaling-engine config, and scaled-plane mask. The header declares plane/CRTC initialization, format/modifier helpers, error accounting, and the `MALIDP_ROTATED_MASK`.

## Control Flow

The header itself has no runtime control flow. Its constants define the config-valid state machine used by `malidp_drv.c` and `malidp_hw.c`: initial, done, and start/update-in-progress. Container macros connect DRM callbacks back to Mali-DP private objects. Plane and CRTC state structs are allocated and copied by the corresponding atomic reset/duplicate/destroy callbacks.

## State And Persistence Behavior

The types in this header define nearly all persistent software state for a Mali-DP instance. `config_valid` and `wq` coordinate commit completion with DE/DC IRQs. `event` stores a pending flip event until the IRQ path sends it. `rotmem_size`, `format`, and prefetch fields persist across duplicated plane state. Coefficient arrays and scaling config persist in CRTC state until changed by an atomic commit.

## Dependencies And Integration Points

The header depends on DRM writeback/encoder types, waitqueues, mutex/spinlock headers, and `malidp_hw.h`. It integrates `malidp_drv.c`, `malidp_crtc.c`, `malidp_planes.c`, `malidp_hw.c`, and `malidp_mw.c` by providing shared state and declarations.

## Risks And Edge Cases

The header defines cross-file contracts: changing state layout or config-valid constants affects IRQ/commit synchronization. Debug fields are conditional on `CONFIG_DEBUG_FS`. `MALIDP_ROTATED_MASK` covers 90/270 degree rotations but not 180, which matches rotation-memory needs but can be easy to misuse. `malidp_plane_state` fields must be copied during state duplication to avoid stale hardware programming.

## Test Signals

Compile coverage with and without debugfs, atomic state duplicate/reset tests, lockdep around error stats, config-valid wait/IRQ tests, rotation-memory checks, and build coverage across all Mali-DP files are the primary validation signals.
