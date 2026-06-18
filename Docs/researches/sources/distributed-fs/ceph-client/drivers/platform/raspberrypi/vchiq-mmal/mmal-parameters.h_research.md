# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-parameters.h

## Purpose

This header defines MMAL parameter IDs and parameter payload structures for the Raspberry Pi VideoCore multimedia stack. It groups common, camera, video, audio, clock, and Miracast parameter namespaces and provides the camera/video/display enums and structs needed by host drivers when calling MMAL port parameter get/set operations.

## Important APIs, Types, And Functions

The important constants are `MMAL_PARAMETER_GROUP_COMMON`, `CAMERA`, `VIDEO`, `AUDIO`, `CLOCK`, and `MIRACAST`. Major enums include common and camera parameter IDs, camera timestamp/exposure/metering/AWB/image-effect modes, flicker avoid modes, video rate control/profile/level IDs, video parameter IDs, mirror/display transform/display mode/display set values. Important payloads are `mmal_parameter_fps_range`, `mmal_parameter_camera_config`, `mmal_parameter_awbgains`, `mmal_parameter_video_profile`, `vchiq_mmal_rect`, `mmal_parameter_displayregion`, `mmal_parameter_imagefx_parameters`, and `mmal_parameter_camera_info`.

## Control Flow

This file provides data contracts only. Runtime flows are through `vchiq_mmal_port_parameter_set()` and `vchiq_mmal_port_parameter_get()` in `mmal-vchiq.c`: callers pass a parameter ID from this header and a matching payload, which is copied into or out of MMAL worker messages.

## State And Persistence

The header owns no mutable state. Its values describe requested or reported VideoCore state: camera configuration, exposure, AWB, image effects, encoder rate control, display layout, and camera inventory. Persistence is firmware/component state and lasts only until changed, component destruction, firmware reset, or device power state changes.

## Dependencies And Integration Points

The file includes `<linux/math.h>` for fractional numeric types. It integrates with MMAL port-parameter message structs in `mmal-msg.h`, with local format/common MMAL headers, and with camera/V4L2 code that translates user-visible controls into MMAL parameter IDs and payloads.

## Risks

Parameter IDs are ABI values; changing order or group arithmetic would silently alter firmware commands. Many enum comments refer to MMAL types not defined in this header, so caller-side payload matching is convention-based. `mmal_parameter_camera_info` uses fixed maxima for camera, flash, and string counts; firmware responses exceeding those assumptions must be bounded by caller buffers. `mmal_parameter_imagefx_parameters` is capped at five values.

## Test Signals

Good tests include setting and reading camera controls, display regions, H.264 encoder parameters, AWB gains, exposure modes, FPS ranges, image effects, and camera info. Boundary tests should exercise parameter get responses larger than the supplied buffer and parameter set payloads near the MMAL worker parameter-space limit.
