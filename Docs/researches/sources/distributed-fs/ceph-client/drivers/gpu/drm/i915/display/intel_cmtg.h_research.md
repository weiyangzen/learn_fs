# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.h

## Purpose

`intel_cmtg.h` exposes the minimal CMTG sanitization API used by display initialization/sanitization code.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_display` and declares `intel_cmtg_sanitize(struct intel_display *display)`. No CMTG state type is exposed because the implementation currently only reads and optionally disables inherited hardware state.

## Control Flow And Integration

Display sanitization callers include this header and call `intel_cmtg_sanitize()` before disabling port PLLs. The implementation handles platform detection, readout, and safe disable internally.

## State And Persistence

The header defines no persistent state. CMTG state remains hardware-only and local to the implementation's readout snapshot.

## Dependencies, Risks, And Test Signals

The low include footprint keeps dependencies minimal. The main API risk is ordering: callers must run the sanitizer while the CMTG clock source is still available. Compile tests catch signature drift; boot tests on CMTG-capable platforms should verify that the sanitizer is invoked and does not disturb active display configurations.
