# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.c

Purpose: main Cedrus VPU platform driver and V4L2 mem2mem device setup. It registers `/dev/video*`, media controller entities, V4L2 controls for stateless codecs, request validation, file operations, SoC variants, OF match data, and runtime PM hooks.

Important APIs/functions: `cedrus_try_ctrl()` validates H264 and HEVC SPS controls, restricting chroma to 4:2:0 and bit depth to hardware capability/current buffer state. `cedrus_controls[]` declares all stateless MPEG2/H264/HEVC/VP8 controls with capability masks. `cedrus_find_control_data()` and `cedrus_get_num_of_controls()` provide per-job control lookup. `cedrus_init_ctrls()` creates only controls supported by `ctx->dev->capabilities`. `cedrus_request_validate()` enforces exactly one buffer per media request. `cedrus_open()` allocates a context, initializes mem2mem queues, default formats, and controls; `cedrus_release()` tears them down. `cedrus_probe()` wires hardware, V4L2, mem2mem, media controller, and video registration. `cedrus_remove()` unwinds runtime resources.

Control flow: platform probe allocates `cedrus_dev`, calls `cedrus_hw_probe()`, registers V4L2 and media devices, initializes `v4l2_m2m_dev`, registers the decoder video node, registers the media controller, and publishes the media device. File open creates a per-file `cedrus_ctx`; queue init is delegated to `cedrus_queue_init()`. Decode jobs later enter through `cedrus_device_run()` from mem2mem ops. Remove cancels watchdog work, unregisters media/V4L2 objects, and releases hardware.

State and persistence: persistent runtime state includes `cedrus_dev` capabilities, mapped base registers, clocks, reset control, mem2mem device, watchdog work, and per-open `cedrus_ctx` controls/formats/codec scratch pointers. No disk state. Capture-buffer codec side data can survive across jobs until streaming stops.

Dependencies/integration: depends on V4L2 controls, media requests, media controller, V4L2 mem2mem, vb2, platform/OF matching, and hardware setup in `cedrus_hw.c`. SoC variants define capability bits and `mod_rate` used by hardware setup.

Risks: request validation only checks buffer count, while codec setup assumes required controls are present and valid. Bit-depth changes are blocked once capture buffers are busy; regressions here can mis-size H265 10-bit capture buffers. Capability-gated controls and formats must stay in sync. Error paths in `cedrus_init_ctrls()` must free partially created handlers and pointer arrays.

Test signals: probe/remove on each compatible, media graph validation, open/close leak tests, request submission with zero/multiple buffers, invalid H264/HEVC SPS controls, HEVC 10-bit buffer allocation behavior on H6-capable variants, and V4L2 compliance for mem2mem/stateless decoder nodes.
