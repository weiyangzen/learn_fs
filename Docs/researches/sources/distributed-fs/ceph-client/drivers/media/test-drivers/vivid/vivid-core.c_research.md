# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.c

## Purpose
`vivid-core.c` is the central module and instance lifecycle implementation for the VIVID virtual video test driver. It creates configurable virtual capture/output/radio/SDR/VBI/metadata/touch devices, exposes shared V4L2 ioctl dispatch, initializes queues/controls/media entities, and tears everything down.

## Important APIs, types, and functions
The file defines many module parameters controlling instance count, device-node numbers, crop/compose/scale modes, planar API, node-type bitmask, input/output counts and types, debug level, allocator choice, cache hints, request support, and error-injection availability.

`vidioc_querycap()` reports aggregate capabilities. Many wrapper ioctls dispatch to subsystem-specific implementations depending on `video_device` type/direction, such as video capture/output, radio, SDR, touch, VBI, and metadata handlers. `vivid_ioctl_ops` collects the broad V4L2 ioctl surface; `vivid_fops` and `vivid_radio_fops` provide file operations.

Lifecycle helpers include `vivid_create_queue()` for vb2 queue initialization, `vivid_detect_feature_set()` for interpreting module parameters into `struct vivid_dev` feature booleans, `vivid_set_capabilities()`, `vivid_disable_unused_ioctls()`, `vivid_init_dv_timings()`, `vivid_create_queues()`, `vivid_create_devnodes()`, and `vivid_create_instance()`. Module probe creates requested instances; remove unregisters every created node and adapter.

## Control flow
`vivid_init()` prebuilds HDMI/S-Video output menu labels, registers a platform device/driver, and creates workqueues. Probe verifies the font, clamps `n_devs`, and calls `vivid_create_instance()` for each instance. Instance creation registers the V4L2/media device, detects enabled features, initializes TPG/EDID/timings/default formats/controls/locks/lists/queues, optionally allocates CEC adapters and starts the CEC thread, sets up controls, creates device nodes, and stores the instance in `vivid_devs`.

Runtime ioctls enter the common operation table and dispatch to the correct subsystem. File release handles disconnect-error reconnection and RDS ownership cleanup before delegating to vb2 or V4L2 fh release.

## State and persistence
Global state includes `vivid_devs[]`, `n_devs`, HDMI/S-Video connection menu strings, output skip masks, and update workqueues. Per-instance state is the large `struct vivid_dev`: controls, device nodes, capabilities, inputs/outputs, vb2 queues, active lists, stream counters, TPG, EDID, timings, framebuffer state, error injection flags, radio/RDS state, CEC state, and connection mappings.

## Dependencies and integration points
The file integrates V4L2 core, media controller, videobuf2 vmalloc/dma-contig allocators, V4L2 TPG, platform devices, font support, CEC, framebuffer OSD, and many VIVID subsystem files. Request validation is media-controller based and can inject validation errors.

## Risks and test signals
Risks are high because module parameters can create many feature combinations; cleanup paths must unregister partially created devices correctly; `vivid_init()` error handling includes a suspicious `platform_driver_register()` call in the `unreg_driver` path where unregister would be expected; and dynamic menu/workqueue updates require careful locking. Test signals include `v4l2-compliance` across node-type combinations, probe/remove loops, CEC/OSD optional builds, request-support modes, allocator/cache-hint combinations, disconnect error injection, and leak checks after partial probe failures.
