# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.c

## Purpose
This file is the main AtomISP CSS 2.x compatibility layer. It adapts the Linux/V4L2-facing atomisp driver to the Intel IA CSS firmware API, including firmware loading, MMIO callbacks, CSS pipe and stream creation, ISP parameter propagation, video/stat/metadata buffer queueing, event dispatch, and allocation/freeing of CSS-owned statistics data.

## Important APIs and Functions
- MMIO callbacks `atomisp_css2_hw_store_*()` and `atomisp_css2_hw_load_*()` serialize ISP register access through `mmio_lock` and are installed into `ia_css_env.hw_access_env`.
- Firmware/CSS lifecycle: `atomisp_css_load_firmware()`, `atomisp_css_init()`, `atomisp_css_uninit()`.
- Pipe/stream lifecycle: `atomisp_create_pipes_stream()`, `atomisp_destroy_pipes_stream()`, `atomisp_css_update_stream()`, `atomisp_css_start()`, `atomisp_css_stop()`.
- Buffer APIs: `atomisp_q_video_buffer_to_css()`, metadata/3A/DIS queue helpers, `atomisp_css_queue_buffer()`, and `atomisp_css_dequeue_buffer()`.
- Statistics/metadata allocation: `atomisp_css_allocate_stat_buffers()`, `atomisp_css_free_stat_buffers()`, `atomisp_alloc_3a_output_buf()`, `atomisp_alloc_dis_coef_buf()`, `atomisp_alloc_metadata_output_buf()`.
- Event handling: `atomisp_css_isr_thread()` routes CSS frame/stat/metadata completions to `atomisp_buf_done()` and queues assert recovery on firmware asserts.

## Control Flow
Firmware setup installs hardware callbacks and loads the CSS firmware, then `atomisp_css_init()` initializes IA CSS with the HMM/MMU base. Format and subdev paths mutate stream and pipe configs. Before streaming, `atomisp_create_pipes_stream()` creates run-mode-valid CSS pipes and binds them to streams. `atomisp_css_start()` starts SP and active streams. During streaming, vb2 queues video and side buffers into CSS, while the IRQ thread drains CSS events and completes buffers. Stream-off calls `atomisp_css_stop()`, which destroys streams/pipes before `ia_css_stop_sp()`, resets raw-buffer/stat/metadata state, and frees queued parameters.

## State and Persistence
Runtime state lives mostly in `asd->stream_env[]` and `asd->params`: IA CSS stream/pipe pointers, configs, stream state, update flags, grid info, CSS parameter blobs, metadata user buffers, DVS state, and side-buffer lists. Device-level state includes firmware/env, MMIO base, CSS initialization status, and global `atomisp_dev` for MMIO callbacks.

## Dependencies and Integration Points
Depends on IA CSS (`ia_css_*`, `sh_css_*`), HMM/MMU glue, AtomISP command helpers, file ops, ioctls, and subdev configuration. It is used by `atomisp_fops.c` for buffer queueing, `atomisp_ioctl.c` for streaming/parameter application, `atomisp_subdev.c` for format-driven CSS config, and `atomisp_csi2.c` for MMIO register writes.

## Risks
CSS object lifetime and ordering are fragile, especially around `ia_css_stop_sp()`. The file assumes caller-side serialization through `isp->mutex` in many paths. Global `atomisp_dev` makes multi-device assumptions risky. User-copy DIS/stat paths must match current grid sizes. Manual list movement between free, in-CSS, and ready stats queues is error-prone. Numerous FIXME/workaround comments indicate firmware and hardware quirks.

## Test Signals
Key signals are successful firmware load/init, stream creation for preview/video/capture/copy modes, correct `ia_css_pipe_get_info()` frame sizes after format changes, vb2 queue/dequeue under sustained streaming, CSS events for output/3A/DIS/metadata, firmware assert recovery scheduling, stream-off then stream-on after reset, and allocation/rollback fault injection.
