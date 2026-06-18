# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.h

## Purpose
`helpers.h` declares the V4L2/HFI helper surface used by Venus decoder and encoder implementation files. It is the public header for buffer lifecycle, stream control, format validation, HFI property setup, and session utility functions implemented in `helpers.c`.

## Important APIs
The header groups declarations for codec checking, V4L2 buffer init/prepare/queue/stop/start, queue error and buffer completion, mem2mem run/abort, HFI buffer requirements, frame-size calculations, resolution/color/format/work-mode/buffer-count/dynamic-buffer/multistream/stride properties, DPB/internal buffer allocation, buffer registration, initial queued buffer processing, timestamp recovery, profile/level get/set, and output-format negotiation.

## Control Flow And Integration
Decoder and encoder queue operations call these helpers to validate vb2 buffers, start HFI streaming, process initial buffers, and stop/cleanup. Control and format setup code calls the property helpers before starting sessions. HFI callbacks call buffer-reference and timestamp helpers to complete buffers correctly.

## State And Persistence
No state is stored in the header. All functions operate on `struct venus_inst`, `struct venus_core`, `vb2_buffer`, and `vb2_v4l2_buffer` state owned elsewhere.

## Dependencies
Includes `media/videobuf2-v4l2.h` and relies on HFI types such as `struct hfi_buffer_requirements` being visible through the including context.

## Risks
- A wide helper API means ordering is caller-sensitive; for example buffer counts, formats, work mode, and internal buffers must be configured before `hfi_session_start()`.
- Several functions return HFI errors directly and callers need consistent cleanup/error propagation.

## Test Signals
Compile tests validate cross-file declarations. Runtime tests should exercise each queue op path in decoder and encoder, plus property programming for supported codecs and formats.
