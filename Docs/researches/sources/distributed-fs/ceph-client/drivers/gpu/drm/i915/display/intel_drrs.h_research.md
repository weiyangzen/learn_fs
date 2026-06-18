<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h

## Purpose
This header declares the DRRS control, frontbuffer notification, initialization, and debugfs APIs for the i915 display driver.

## Important APIs, Types, and Functions
The exported declarations cover capability checks, string conversion, activation/deactivation, frontbuffer invalidate/flush handling, CRTC initialization, and CRTC/connector debugfs registration. It forward declares `enum drrs_type`, `enum transcoder`, and the Intel display/connector/CRTC state types.

## Control Flow
There is no local control flow. The API shape reflects the runtime flow: initialize per CRTC, activate on a suitable committed state, update from frontbuffer tracking, deactivate on modeset/disable, and expose status through debugfs.

## State and Persistence Behavior
No state is stored in the header. The functions operate on per-CRTC DRRS state embedded in display types.

## Dependencies and Integration Points
It is included by panel, frontbuffer, atomic modeset, and debugfs code that need to coordinate DRRS. Keeping forward declarations minimal reduces compile coupling with full display type definitions.

## Risks
Callers must pass the correct CRTC state and frontbuffer masks; the header cannot enforce joiner or active-state checks. Debugfs helpers should only be registered for initialized connectors/CRTCs.

## Test Signals
Compile coverage, debugfs node presence for DRRS-capable panels, and frontbuffer notification paths linking successfully against the DRRS implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h -->
