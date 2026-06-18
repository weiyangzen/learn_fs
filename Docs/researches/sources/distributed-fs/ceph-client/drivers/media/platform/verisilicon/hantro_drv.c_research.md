# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_drv.c

## Purpose
Implements the platform driver, V4L2 mem2mem device lifecycle, queue initialization, control registration, codec job scheduling, IRQ completion handoff, watchdog timeout handling, media-controller topology, runtime PM, and device-tree matching for Hantro encoder/decoder instances.

## Important APIs, Types, And Functions
Public helpers include `hantro_get_ctrl`, `hantro_get_ref`, `hantro_irq_done`, `hantro_watchdog`, `hantro_start_prepare_run`, and `hantro_end_prepare_run`. Internal anchors include `device_run`, `queue_init`, `hantro_ctrls_setup`, `hantro_open`, `hantro_release`, `hantro_probe`, `hantro_remove`, and media entity helpers. The `controls[]` table declares JPEG, MPEG2, VP8, H264, HEVC, VP9, and AV1 stateless controls.

## Control Flow And State
Open allocates `hantro_ctx`, initializes V4L2 m2m queues, resets formats, and installs controls matching encoder or decoder capability bits from the variant. Job execution resumes runtime PM, enables clocks, copies source metadata to destination, and calls `ctx->codec_ops->run`. Codec runs call start/end prepare helpers to bind request controls and enable/disable postproc. Completion comes from IRQ or watchdog; it cancels work, invokes codec `done` on success, disables clocks, updates buffer sequences, handles EOS draining, and finishes the m2m job.

## Dependencies And Integration Points
The file integrates with platform DT compatibles, media controller links, V4L2 requests, videobuf2 DMA-contig queues, pm_runtime, clk/reset frameworks, and variant tables defined by SoC-specific files outside this work item.

## Risks And Test Signals
`device_run` uses `hantro_job_finish_no_pm` for all error exits, including after runtime PM or clocks may already be active; PM/clock error-path tests are useful. Control validation rejects unsupported H264 chroma/bit depth, HEVC bit depths outside 8/10, VP9 non-profile-0, and AV1 non-8/10. Important tests include request API decode, EOS draining, timeout reset, shared-device scheduling, media graph enumeration, and probe/remove under missing clocks/IRQs/register resources.
