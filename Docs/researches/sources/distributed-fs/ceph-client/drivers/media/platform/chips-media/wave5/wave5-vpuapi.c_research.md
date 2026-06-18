# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.c

## Purpose
Implements the higher-level Wave5 API used by V4L2 encoder/decoder frontends. It serializes firmware/backend calls, validates parameters, tracks codec instance state, manages firmware open/close, sequence init, bitstream pointers, frame-buffer registration, encode/decode command submission, output result conversion, and command-style state updates.

## Important APIs, Types, and Functions
Initialization functions include `wave5_vpu_init_with_bitcode()`, `wave5_initialize_vpu()`, and `wave5_vpu_get_version_info()`. Decoder APIs cover `wave5_vpu_dec_open()`, `wave5_vpu_dec_close()`, sequence init/complete, frame-buffer registration, bitstream buffer query/update, decode start, rd pointer management, output info, display flag management, reset framebuffer, and `wave5_vpu_dec_give_command()`. Encoder APIs cover `wave5_vpu_enc_open()`, `wave5_vpu_enc_close()`, frame-buffer registration, parameter checking, `wave5_vpu_enc_start_one_frame()`, output info, `wave5_vpu_enc_give_command()`, and sequence init/complete.

## Control Flow
All hardware/firmware calls are wrapped by `vpu_dev->hw_lock`. Firmware init resets the VPU unless already initialized, in which case it reinitializes and returns busy. Decoder open validates bitstream alignment and initializes circular stream pointers. Decoder close loops `dec_finish_seq`, handles still-running firmware by collecting output, then frees work/task/auxiliary DMA. Encoder open validates open parameters and builds firmware state. Encoder stream submission stores PTS by source index and calls `wave5_vpu_encode()`. Encoder output reads firmware result and restores PTS from the map. Close loops `enc_finish_seq` until firmware exits or retry limit expires, then frees work, task, sub-sampled, MV, and FBC buffers.

## State and Persistence
This file mutates `inst->codec_info->dec_info` and `enc_info`: open parameters, stream pointers, initial sequence info, display flags, registered buffer counts, stride, PTS map, queue counters, and DMA buffer handles. It also gates global VPU state through `vpu_device->hw_lock`. No disk persistence exists.

## Dependencies and Integration Points
Depends on backend functions declared in `wave5.h`, register definitions, VDI DMA helpers, runtime PM, and Wave5 error/config constants. It is the bridge between V4L2-facing frontend files and firmware command implementation.

## Risks
Several close error paths call `pm_runtime_resume_and_get()` where a put was likely intended, making PM reference leaks a review target. `pts_map` indexes by `src_idx` and assumes firmware returns indices within its fixed size. Decoder circular buffer arithmetic must preserve one-byte empty space and reject overlap. Retry loops depend on firmware fail reasons being precise. `wave5_vpu_dec_reset_framebuffer()` returning `-EINVAL` for empty slots is used as a loop terminator in callers.

## Test Signals
Unit-like fault injection around mutex interruption, firmware busy retries, close while frames are pending, circular bitstream wraparound, invalid alignment/size parameters, PTS propagation across reordered jobs, sequence-change decode streams, and PM refcount checks.
