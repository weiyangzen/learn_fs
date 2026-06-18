# sources/distributed-fs/ceph-client/drivers/staging/greybus/camera.c

## Purpose
Implements the Greybus camera management driver for camera-class bundles. It exposes module camera operations through `gb_camera_module`, translates host camera requests into Greybus camera protocol messages, and manages a separate offloaded camera data CPort and AP CSI transmitter when streams are configured.

## Important APIs, Types, And Functions
Key state is `struct gb_camera`, holding management and data `gb_connection` objects, the module bundle, data CPort ID, a mutex, configured/unconfigured state, debugfs buffers, and registered `gb_camera_module`. Format translation is table-driven by `gb_camera_fmt_info`. Main protocol helpers are `gb_camera_capabilities()`, `gb_camera_configure_streams()`, `gb_camera_capture()`, and `gb_camera_flush()`. `gb_cam_ops` adapts those helpers to the host-facing camera-module API. `gb_camera_setup_data_connection()` creates the offloaded CSI data path and configures AP CSI output through `gb_hd_output()`.

## Control Flow
`gb_camera_probe()` requires exactly two CPorts, one camera management and one camera data, creates the management connection with `gb_camera_request_handler()`, initializes debugfs, registers the camera module, and drops the runtime-PM reference. Configuration sends `GB_CAMERA_TYPE_CONFIGURE_STREAMS`, validates returned padding and stream count, tears down any prior data connection, and either returns adjusted/test-only results or creates the data connection, switches UniPro links to high speed, programs CSI, and marks the device configured. Disconnect unregisters the module and destroys both connections.

## State And Persistence
State is in-memory only. The configured state pins runtime PM with an extra no-resume reference until streams are unconfigured. Debugfs keeps last operation outputs in per-operation page-sized buffers. CSI clock, lane count, data connection state, and power mode are reconstructed each configuration cycle.

## Dependencies And Integration Points
Depends on Greybus core, AP bridge output requests, Greybus SVC power-mode control, V4L2 media-bus pixel codes, debugfs, and the external camera-module registry declared in `gb-camera.h`. It integrates with runtime PM at the Greybus bundle level.

## Risks
Hard-coded ES2/AP CSI assumptions and fixed four-lane CSI setup limit portability. Response copy in `gb_camera_operation_sync_flags()` trusts the allocated response buffer sizing discipline. Debugfs operations can drive real protocol state and should stay restricted to debugging. Correct runtime-PM balance is critical around configured streams and error unwinds.

## Test Signals
Probe should reject malformed CPort layouts. Exercise capabilities, test-only configure, adjusted configure, real configure/unconfigure, capture, flush, metadata events, suspend/resume with and without a data connection, and all data-connection error unwind paths. Debugfs read/write operations provide manual smoke tests.
