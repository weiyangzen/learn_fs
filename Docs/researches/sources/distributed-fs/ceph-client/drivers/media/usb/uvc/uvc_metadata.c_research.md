# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_metadata.c

Purpose: implements UVC metadata capture node registration and metadata format negotiation. It exposes a V4L2 metadata capture device per stream and detects Microsoft UVC 1.5 extension-unit metadata support.

Important APIs and functions: exported functions are `uvc_meta_register` and `uvc_meta_init`. V4L2 ioctl handlers are `uvc_meta_v4l2_querycap`, `uvc_meta_v4l2_get_format`, `uvc_meta_v4l2_try_format`, `uvc_meta_v4l2_set_format`, and `uvc_meta_v4l2_enum_formats`. Detection helpers are `uvc_meta_find_msxu` and `uvc_meta_detect_msxu`.

Control flow: `uvc_meta_init` probes for an MSXU entity with `UVC_GUID_MSXU_1_5`, reads current metadata control state, and if needed tries to enable metadata by reading `GET_MAX` and writing that value with `SET_CUR`. It then fills the device metadata format array with generic `V4L2_META_FMT_UVC`, optional device-info metadata format such as RealSense D4XX, and optional `V4L2_META_FMT_UVC_MSXU_1_5`. `uvc_meta_register` initializes stream metadata defaults and calls the common `uvc_register_video_device` path with metadata file/ioctl operations. Format setting validates requested type, picks a supported dataformat, enforces minimum buffer size, and refuses changes while the metadata vb2 queue is busy.

State and persistence: stream metadata state is `stream->meta.format`, `stream->meta.buffersize`, and its vb2 queue/video node. Device metadata support is stored in `dev->meta_formats`, `dev->nmeta_formats`, and possibly `UVC_QUIRK_MSXU_META`. The MSXU enable write changes device runtime state but is not persisted by this file.

Dependencies and integration points: depends on V4L2 metadata APIs, vb2 vmalloc queues through `uvc_queue.c`, UVC extension-unit queries through `uvc_query_ctrl`, and the common video-device registration helper in `uvc_driver.c`. Actual metadata payload filling is done by the streaming implementation.

Risks: enabling MSXU metadata writes to device controls during probe and silently treats most query failures as lack of support. Metadata node registration failures are ignored by `uvc_register_terms`, so video capture can work without metadata. Buffer sizes are user-influenced but clamped only to a minimum; downstream payload writers must respect vb2 plane size.

Test signals: enumerate metadata formats on ordinary UVC and RealSense devices, verify MSXU metadata enablement and format exposure, set metadata buffer size before streaming, confirm `-EBUSY` during streaming, stream video plus metadata and validate payload parseability, and test video registration when metadata registration fails.
