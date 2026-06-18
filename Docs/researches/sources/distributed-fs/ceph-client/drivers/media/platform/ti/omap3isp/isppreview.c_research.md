# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.c

## Purpose
`isppreview.c` implements the OMAP3 ISP preview engine subdevice. The preview engine performs Bayer/greyscale to YUV processing with configurable CFA interpolation, gamma, noise filtering, defect correction, white balance, color conversion, luma/chroma processing, brightness/contrast, crop handling, memory input/output, and resizer forwarding.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_preview_init()`, `omap3isp_preview_cleanup()`, `omap3isp_preview_register_entities()`, `omap3isp_preview_unregister_entities()`, `omap3isp_preview_isr()`, `omap3isp_preview_isr_frame_sync()`, `omap3isp_preview_busy()`, and `omap3isp_preview_restore_context()`.
- Parameter programming: numerous `preview_config_*()` and `preview_enable_*()` helpers write tables and registers for luma, inverse A-law, median filter, CFA, chroma suppression, white balance, black adjustment, RGB blending, CSC, YC limits, defect correction, dark frame, noise filter, gamma, contrast, and brightness.
- Shadow state: `preview_params_lock()`, `preview_params_unlock()`, `preview_params_switch()`, `preview_config()`, and `preview_setup_hw()` implement double-buffered parameter updates protected by a spinlock.
- Format/crop: `preview_try_format()`, `preview_try_crop()`, enum/get/set format operations, and selection operations constrain input formats, output YUV formats, and hidden hardware margins.
- Streaming/buffers: `preview_configure()`, `preview_enable_oneshot()`, `preview_set_stream()`, `preview_isr_buffer()`, `preview_video_queue()`, and address/offset helpers coordinate one-shot hardware runs with memory queues and SBL paths.
- Media integration: `preview_link_setup()` enforces either CCDC or memory input and either resizer or memory output.

## Control Flow
Initialization sets default image-processing tables and parameters, creates controls for brightness/contrast, initializes media pads, default formats/crop, and video input/output nodes. Userspace private preview config copies enabled feature structs from userspace into inactive shadow parameter sets, marks updates, and switches them when neither active nor shadow copies are busy. Stream start enables the preview subclock, configures input/output format, crop margins, SBL bandwidth, active parameter registers, output port bits, offsets, YUV byte order, and then starts one-shot execution as required. Interrupt handling applies pending shadow updates, recomputes input-size margins, rotates memory buffers, marks pipeline idle input/output, and restarts one-shot operation for continuous pipelines.

## State And Persistence
Persistent state lives in `struct isp_prev_device`: media subdev/pads, active formats, crop rectangle, V4L2 controls, input/output routing, video queues, stream state, wait/stop primitives, and the nested double-buffered `params` object. The hardware register context is restored through `omap3isp_preview_restore_context()` by marking all features for update and reprogramming them from cached state.

## Dependencies And Integration Points
This file depends on V4L2 subdev, controls, and media entity APIs; ISP register helpers and SBL controls; pipeline timing/rate state; `ispvideo` buffer queues; format metadata from `omap3isp_video_format_info()`; table headers (`cfa_coef_table.h`, `gamma_table.h`, `noise_filter_table.h`, `luma_enhance_table.h`); and register macros from `ispreg.h`. It connects upstream to CCDC or memory and downstream to resizer or memory capture.

## Risks And Edge Cases
- The preview engine is used in one-shot mode even for continuous operation; correct restart on ISR/frame-sync and underrun flags is critical.
- Hidden crop margins depend on enabled features and Bayer/non-Bayer format; bugs can cause line/frame overflow or Bayer pattern shifts.
- Userspace config copying uses pointers inside `omap3isp_prev_update_config`; each feature needs correct offset/size metadata in `update_attrs`.
- Double-buffered parameter bit logic is subtle and concurrency-sensitive because config ioctls and ISR updates share state.
- Memory input has a documented 64-byte alignment hardware bug despite a nominal 32-byte TRM requirement.

## Test Signals
Strong tests include format/crop clamping for all input/output formats, hidden margin calculations with feature combinations, brightness/contrast V4L2 control updates, private config copy fault injection, shadow-parameter switch races, stream start/stop for memory and CCDC input, memory and resizer output link exclusivity, buffer underrun restart, context restore, and register-programming snapshots for default parameters.
