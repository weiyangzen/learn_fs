# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.c

## Purpose
Calculates firmware/internal buffer sizes and buffer counts for Iris decode and encode sessions across codecs and VPU generations. It is the sizing oracle for BIN, COMV, NON_COMV, LINE, PERSIST, DPB, SCRATCH, VPSS, ARP, and PARTIAL buffers.

## Important APIs And Functions
- Decode sizing helpers cover H.264/HEVC/VP9/AV1 BIN buffers, COMV, persistent buffers, non-COMV, line buffers, AV1 IBC/PARTIAL buffers, DPB split mode, and VPU4x-specific VP9/persist line sizing.
- Encode sizing helpers cover bitstream/bin buffers, COMV, non-COMV, line buffers, VPU33/VPU4x line variants, DPB/reference/UBWC metadata, ARP, VPSS/scaling, SCRATCH1, and SCRATCH2.
- `is_scaling_enabled()` detects encoder scaling from source and destination dimensions.
- `output_min_count()` chooses decoder capture minimum counts, including firmware-provided reconfig counts and VP9/AV1 defaults.
- `struct iris_vpu_buf_type_handle` maps Iris buffer types to size functions.
- `iris_vpu_buf_size()` dispatches base VPU2/VPU3 sizes for decoder/encoder.
- `iris_vpu33_buf_size()` reuses base decoder sizing but overrides encoder LINE sizing for VPU33.
- `iris_vpu4x_buf_size()` provides VPU4x-specific decoder and encoder sizing dispatch.
- `iris_vpu_buf_count()` returns required counts for user and internal buffer types.

## Control Flow And Integration Points
Codec init and format setters call `iris_get_buffer_size()`/`iris_vpu_buf_count()` through higher-level buffer helpers to set V4L2 `sizeimage` and min counts. Stream-on code creates internal buffers according to platform internal-buffer tables and these size/count calculations. Platform data selects the generation-specific top-level sizing function through `.get_vpu_buffer_size`. vb2 prepare validates user buffer plane sizes against computed sizes.

## State And Persistence Behavior
The file does not allocate buffers itself. It reads mutable session state: domain, codec, formats, crop, firmware caps (`STAGE`, `DRAP`, `ROTATION`), `hfi_rc_type`, firmware min output count, output buffer count, platform pipe count, and platform caps. Returned sizes influence persistent per-session buffer metadata and actual DMA allocations elsewhere.

## Dependencies
Depends on `iris_instance.h`, `iris_vpu_buffer.h`, HFI gen1/gen2 define constants, V4L2 pixel formats, firmware cap values, and platform `num_vpp_pipe`/caps.

## Risks
- Many calculations use 32-bit arithmetic on width/height/products; high resolutions or bad inputs can overflow before alignment.
- Codec-specific constants from HFI headers must match firmware expectations exactly; undersizing internal buffers can cause firmware memory corruption or decode/encode failure.
- Rotation changes encoder bitstream width/height and therefore internal buffer sizes; dynamic rotation must be synchronized with allocation timing.
- DRAP/AV1 and split-mode branches alter COMV/PERSIST/DPB sizes; mismatched control values and buffer creation can under-allocate.
- VPU4x encoder sizing uses `inst->codec` where helper logic appears to expect HFI encode-standard constants, requiring careful validation before enabling.

## Test Signals
- Unit-style size checks for representative resolutions/codecs/pipe counts against firmware reference values.
- End-to-end decode for H.264/HEVC/VP9/AV1 at 1080p, 4K, and 8K-class limits.
- Encoder tests for H.264/HEVC, stage 1/2, CBR/VBR/CQ, rotation 90/270, scaling, and crop.
- DRC tests where `fw_min_count` changes output count and DPB count.
- KASAN/KFENCE and firmware error logs during stream-on catch under-allocation.
