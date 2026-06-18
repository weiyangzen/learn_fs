# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.h

## Purpose
Central Wave5 API and state header. It defines product IDs, codec standards, instance states, firmware constants, codec command enums, frame-buffer and geometry structures, decoder/encoder parameter/result structures, device/instance state structures, and prototypes for VDI and API operations.

## Important APIs, Types, and Functions
Important types include `struct vpu_device`, `struct vpu_instance`, `struct dec_info`, `struct enc_info`, `struct frame_buffer`, `struct dec_open_param`, `struct dec_initial_info`, `struct dec_output_info`, `struct enc_wave_param`, `struct enc_open_param`, `struct enc_param`, and `struct enc_output_info`. Constants define framebuffer limits, work-buffer sizing formulas, bitstream buffer rules, profile/level values, reset modes, interrupts, frame maps, queue status, EOS sentinel indices, and codec commands.

## Control Flow
The header itself has no runtime flow but defines the state machine used by frontends: `NONE`, `OPEN`, `INIT_SEQ`, `PIC_RUN`, and `STOP`. API prototypes split flow into init/version, decoder open/sequence/register/decode/output/close, and encoder open/sequence/register/encode/output/close.

## State and Persistence
`struct vpu_device` owns persistent platform lifetime state: V4L2 devices, mem2mem devices, instance list, locks, product data, common memory, SRAM, register base, clocks, reset, IRQ/polling state, and ID allocator. `struct vpu_instance` owns per-open state: formats, controls, completion, kfifo, codec info union pointer, frame buffers, bitstream buffer, EOS/retry flags, crop, frame rate, rate-control and encoder parameters.

## Dependencies and Integration Points
Includes kfifo, IDA, genalloc, V4L2 device/mem2mem/controls, Wave5 VDI, config, and error headers. It is consumed by all Wave5 frontend and backend implementation files.

## Risks
ABI-like coupling is high: changing structures affects many C files. Fixed array sizes (`WAVE5_MAX_FBS`, `MAX_REG_FRAME`, `pts_map[32]`) must match firmware and V4L2 buffer assumptions. The header contains a duplicated `vdb_register` field in `struct vpu_device`, which is a compile-time or maintenance concern depending on the exact source baseline. Bitfield packing is compiler-defined but confined to kernel C usage.

## Test Signals
Build all Wave5 objects with sparse/W=1, run structure-user compile coverage for encoder/decoder, validate max buffer counts, exercise all state transitions, and verify firmware result indices never exceed fixed arrays.
