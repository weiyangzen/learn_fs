<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h

## Purpose
This header declares the legacy DVO initialization hook and provides a no-op stub when the i915 build symbol is not enabled.

## Important APIs, Types, and Functions
It forward declares `struct intel_display` and exposes `intel_dvo_init()` under `#ifdef I915`; otherwise an inline stub does nothing.

## Control Flow
There is no local runtime flow except the build-time selection of real initialization versus no-op.

## State and Persistence Behavior
No state is stored here. The implementation allocates encoder/connector state only when built in and when a DVO device probes successfully.

## Dependencies and Integration Points
It is included by display probe code that wants to call DVO init unconditionally while allowing build configurations without i915 DVO support.

## Risks
The stub can hide missing DVO support in non-i915 builds by design. Real callers should not expect an encoder to appear unless probing succeeds.

## Test Signals
Compile coverage with and without `I915`, and display probe logs showing DVO init attempts only in supported builds/platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h -->
