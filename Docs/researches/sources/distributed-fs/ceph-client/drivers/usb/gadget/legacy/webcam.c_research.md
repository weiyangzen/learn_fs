# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/webcam.c

Purpose: legacy `g_webcam` UVC composite gadget with built-in video-control and streaming descriptors for YUY2 and MJPEG at 360p and 720p.

Important APIs, types, and functions: module parameters `streaming_interval`, `streaming_maxpacket`, and `streaming_maxburst` configure the isochronous streaming endpoint. Static UVC descriptors define camera terminal, processing unit, output terminal, input header, uncompressed YUY2 formats, MJPEG formats, frame intervals, and color matching. `webcam_bind` gets the `"uvc"` function instance, fills `struct f_uvc_opts`, builds configfs-style linked lists of formats/frames/header, assigns string IDs, and registers `webcam_config_driver`. `webcam_config_bind` adds the UVC function; `webcam_unbind` releases it.

Control flow: bind wires static descriptor arrays and runtime linked-list metadata into UVC function options before adding the single configuration. The UVC function then owns video request handling and streaming behavior. Composite options may override descriptor strings and IDs.

State and persistence: descriptor objects are static. Linked lists are initialized at bind time using global nodes, so the module assumes one active binding. UVC runtime state, video device behavior, and streaming queues live in `u_uvc`. No persistent state is stored.

Dependencies and integration points: depends on libcomposite, USB video class descriptors, `u_uvc`, and `uvc_configfs` data structures. It integrates with V4L2/UVC gadget userspace through the UVC function implementation.

Risks: static descriptor graphs must remain internally consistent in frame counts, indexes, intervals, and header references. Module parameter bounds are described but not strongly validated here, so invalid endpoint settings may fail later or produce bad descriptors. Re-initializing global list nodes would be risky if multiple bindings were ever allowed.

Test signals: enumerate at full/high/super speed, inspect UVC descriptors with `lsusb -v`, open the host camera, stream YUY2 and MJPEG modes at both advertised resolutions, vary streaming endpoint parameters, disconnect during streaming, and unload while ensuring UVC function references are released.
