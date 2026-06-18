# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-enc.c

## Purpose
Implements the V4L2 mem2mem encoder frontend for the Chips&Media Wave5 VPU. It exposes HEVC/H.264 capture formats, raw YUV output formats, V4L2 controls, vb2 queue handling, encoder stream state transitions, and the mem2mem `device_run` callback that submits one encode job to firmware.

## Important APIs, Types, and Functions
Key exported integration points are `wave5_vpu_enc_register_device()` and `wave5_vpu_enc_unregister_device()`, called by the platform driver. `wave5_vpu_open_enc()` allocates `struct vpu_instance`, initializes V4L2 controls, formats, completion, kfifo, mem2mem context, SRAM, and instance IDs. `wave5_vpu_enc_release()` delegates cleanup to common release logic. Runtime path functions include `wave5_vpu_enc_start_streaming()`, `wave5_vpu_enc_stop_streaming()`, `wave5_vpu_enc_device_run()`, `start_encode()`, and `wave5_vpu_enc_finish_encode()`. Format/ioctl handlers validate stepwise dimensions and maintain `src_fmt`, `dst_fmt`, crop/conformance window, colorimetry, and frame rate. The long `wave5_vpu_enc_s_ctrl()` maps V4L2 MPEG controls into `inst->enc_param` and encoder flags.

## Control Flow
Open creates an encoder instance and default NV12-to-HEVC format. OUTPUT stream-on opens the firmware instance with `wave5_set_enc_openparam()`. Once both queues stream, sequence init is issued, `wave5_vpu_wait_interrupt()` waits for firmware completion, sequence info sets minimum source/FBC buffer counts, compressed frame buffers are allocated and registered, and state advances to `PIC_RUN`. Each mem2mem job calls `start_encode()`, maps source/destination DMA addresses into `struct enc_param`, removes the source buffer from the ready queue by index, and lets the IRQ completion path finish it after firmware reports `enc_src_idx`. `wave5_vpu_enc_finish_encode()` retrieves firmware output, finishes the source vb2 buffer, removes and completes the destination buffer, marks frame type flags, handles firmware EOS via `RECON_IDX_FLAG_ENC_END`, queues `V4L2_EVENT_EOS`, and calls `v4l2_m2m_job_finish()`.

## State and Persistence
State is per open file in `struct vpu_instance`: V4L2 formats, crop window, colorimetry, frame rate, rate-control values, codec standard, vb2 sequence counters, FBC frame buffers, timestamp, and `VPU_INST_STATE_*`. Persistent device state is shared through `struct vpu_device` and firmware-side `enc_info`. No on-disk state is written.

## Dependencies and Integration Points
Depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events, Wave5 helper APIs (`wave5_vpu_enc_*`), common helper code from `wave5-helper.h`, and runtime PM. It integrates with the platform driver through video registration and with interrupt handling through `inst->ops->finish_process`.

## Risks
State transitions are enforced but failures after partial open/sequence init must return queued buffers correctly. Source buffer completion relies on firmware returning a valid `enc_src_idx`; stale or invalid indices can leave buffers active. FBC allocation failure cleanup calls decoder-named reset helpers, which is intentional shared cleanup but worth regression coverage. Runtime PM return values from `pm_runtime_resume_and_get()` are not consistently checked. Control mappings are broad and can silently preserve incompatible combinations until firmware validation.

## Test Signals
Exercise `v4l2-compliance` mem2mem ioctls, HEVC/H.264 encode smoke tests with NV12/NV21/NV16 multi-plane and single-plane inputs, EOS drain with and without final source buffers, streamoff during active jobs, format changes before queue allocation, crop bounds, profile/level/QP/rate-control controls, and error injection for firmware queueing failure and missing destination buffers.
