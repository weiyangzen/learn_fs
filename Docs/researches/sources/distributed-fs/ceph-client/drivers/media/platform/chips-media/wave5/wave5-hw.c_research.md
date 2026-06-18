# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-hw.c

## Purpose
`wave5-hw.c` is the hardware and firmware command backend for the Wave5 driver. It translates high-level decoder and encoder API requests into MMIO register programming, firmware commands, command/result queries, reset and sleep/wake sequences, framebuffer registration, bitstream pointer updates, and capability discovery.

## Important APIs and Functions
Core helpers include `wave5_vpu_is_init`, `wave5_vpu_get_product_id`, `wave5_vpu_init`, `wave5_vpu_re_init`, `wave5_vpu_sleep_wake`, `wave5_vpu_reset`, `wave5_vpu_get_version`, `wave5_vpu_clear_interrupt`, and internal command helpers such as `wave5_bit_issue_command`, `send_firmware_command`, and `wave5_send_query`. Decoder-facing APIs include `wave5_vpu_build_up_dec_param`, `wave5_vpu_dec_init_seq`, `wave5_vpu_dec_get_seq_info`, `wave5_vpu_dec_register_framebuffer`, `wave5_vpu_decode`, `wave5_vpu_dec_get_result`, display flag operations, bitstream flag operations, and read pointer get/set. Encoder-facing APIs include build-up, init sequence, sequence info, framebuffer registration, encode, encode result, finish sequence, and open-parameter validation.

## Control Flow
Initialization writes firmware into the common DMA buffer, clears command registers, programs remap pages, code/temp buffers, AXI parameters, product-specific task buffers, starts the VPU, checks firmware queue status, queries properties, and enables interrupts based on supported encoders/decoders. Runtime commands write mailbox registers, issue a command, poll busy status, then read success/fail registers. Decode flow creates an instance, initializes sequence, queries stream properties, registers compressed and linear framebuffers, sends picture commands, and queries output info. Encode flow similarly creates an instance, writes sequence/GOP/rate-control/crop/source parameters, registers reconstruction buffers, starts picture encode, and queries produced bitstream metadata.

## State and Persistence
Persistent driver state lives in `struct vpu_device` and `struct vpu_instance` codec info. This file updates common DMA memory, SRAM usage, work buffers, task buffers, stream read/write pointers, queue counts, sequence information, framebuffer auxiliary buffers, support flags, performance cycle counters, encoder open parameters, and firmware-visible display flags.

## Dependencies and Integration
It depends on `wave5-regdefine.h` for register offsets, `wave5-vdi` accessors for MMIO and DMA memory, `wave5-vpuapi` data structures, Linux polling helpers, bitfield helpers, and firmware command semantics. It is called by `wave5-vpuapi.c`, decoder/encoder V4L2 frontends, and platform probe/power management code.

## Risks and Test Signals
Risks include timeout handling, overlapping mailbox offsets, product-specific differences between WAVE515 and WAVE521 variants, DMA allocation cleanup on partial failures, secondary AXI size calculations marked TODO, queue count synchronization, 32-bit register writes of DMA addresses, and strict validation needed before firmware commands. Test signals include firmware boot/reinit/sleep/wake/reset on each product, decode/encode sequence init and frame runs, dynamic resolution changes, 8-bit and 10-bit capability checks, framebuffer allocation failure injection, queueing failure retry behavior, and media compliance with real H264/HEVC streams.
