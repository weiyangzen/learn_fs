# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.h

## Purpose
Small driver-facing header for Wave5 V4L2 frontend code. It defines buffer wrappers, format metadata, helpers for converting file/control handles to `struct vpu_instance`, device registration prototypes, and the shared "both queues streaming" predicate.

## Important APIs, Types, and Functions
Defines `struct vpu_src_buffer`, `struct vpu_dst_buffer`, `enum vpu_fmt_type`, and `struct vpu_format`. Inline helpers include `wave5_to_vpu_inst()`, `file_to_vpu_inst()`, `wave5_ctrl_to_vpu_inst()`, `wave5_to_vpu_src_buf()`, `wave5_to_vpu_dst_buf()`, and `wave5_vpu_both_queues_are_streaming()`. It declares encoder/decoder register/unregister functions and `wave5_vpu_wait_interrupt()`.

## Control Flow
No executable control flow beyond inline conversions and queue state checks. The queue predicate obtains capture/output queues from the mem2mem context and returns true only if both vb2 queues are streaming.

## State and Persistence
The header defines wrappers around V4L2 mem2mem buffers with flags such as `consumed` and `display`, but it does not allocate or persist state itself.

## Dependencies and Integration Points
Includes V4L2 controls, ioctl, events, file handles, vb2 V4L2, DMA-contig, vmalloc, `wave5-vpuconfig.h`, and `wave5-vpuapi.h`. It is the shared include for Wave5 encoder, decoder, and platform/frontend helpers.

## Risks
Container conversions assume exact embedding of fields in `struct vpu_instance` and buffer structs. `wave5_vpu_both_queues_are_streaming()` assumes a valid initialized mem2mem context.

## Test Signals
Compile coverage across encoder and decoder builds, open/close path tests that exercise handle conversion, and stream-on ordering tests for the both-queues predicate.
