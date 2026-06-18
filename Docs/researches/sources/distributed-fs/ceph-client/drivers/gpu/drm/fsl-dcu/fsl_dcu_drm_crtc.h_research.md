# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.h

## Purpose
This header declares the Freescale DCU CRTC creation function and forward-declares the driver device structure. It is the interface used by the KMS setup code to instantiate the DCU CRTC.

## Important APIs, Types, and Functions
The header provides the include guard `__FSL_DCU_DRM_CRTC_H__`, forward declaration `struct fsl_dcu_drm_device;`, and prototype `int fsl_dcu_drm_crtc_create(struct fsl_dcu_drm_device *fsl_dev);`.

## Control Flow
There is no executable flow. During KMS initialization, caller code includes this header and invokes `fsl_dcu_drm_crtc_create()` to create planes and register the CRTC.

## State and Persistence Behavior
The header stores no state. The function contract expects the caller to pass an initialized `struct fsl_dcu_drm_device` with DRM device, regmap, connector, and clock resources ready for CRTC setup.

## Dependencies and Integration Points
The direct integration point is `fsl_dcu_drm_kms.c`. The implementation integrates with plane setup, CRTC helper funcs, regmap, and clock programming, but this header keeps those details private.

## Risks
The forward declaration hides required initialization details, so misuse is possible if a caller invokes creation before the DRM device, connector, pixel clock, or regmap are ready. Build coverage should catch signature drift between header and implementation.

## Test Signals
Compile all FSL DCU objects, verify KMS setup calls this function once, and test CRTC creation success and failure paths through driver probe on DCU device-tree platforms.
