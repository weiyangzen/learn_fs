# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.h

## Purpose

`rzg2l_du_drv.h` defines the top-level RZ/G2L DU device model, output identifiers, routing metadata, and conversion helper used across the driver.

## Important APIs, Types, and Functions

`enum rzg2l_du_output` names DSI0 and DPAD0. `rzg2l_du_output_routing` maps output IDs to possible CRTCs and DT ports. `rzg2l_du_device_info` contains the available channel mask and route array. `rzg2l_du_device` stores the Linux device, SoC info, MMIO, DRM device, one CRTC, and one VSP. `to_rzg2l_du_device()` and `rzg2l_du_output_name()` are the public helpers.

## Control Flow

Probe fills `rzg2l_du_device`, KMS init reads its routing data to create CRTCs/VSPs/encoders, and encoder code uses output names for diagnostics.

## State and Persistence Behavior

The structure persists for the platform device lifetime. Compile-time constants cap the driver to one CRTC, one VSP, and one DSI.

## Dependencies and Integration Points

It includes DRM device definitions and local CRTC/VSP headers, making it the central include for driver-private state.

## Risks and Edge Cases

The maximum counts encode current hardware support; adding multi-channel SoCs requires coordinated changes across arrays, routing, and modeset init loops.

## Test Signals

Compile-time coverage and probe tests for every route table validate this header's assumptions.
