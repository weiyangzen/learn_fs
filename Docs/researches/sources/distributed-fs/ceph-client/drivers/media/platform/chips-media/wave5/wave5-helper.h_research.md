# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.h

## Purpose
`wave5-helper.h` declares the shared helper API used by Wave5 decoder and encoder source files. It keeps common V4L2, queue, format, and cleanup helpers in one interface.

## Important APIs and Types
The header includes `wave5-vpu.h`, defines `FMT_TYPES` as 2 and `MAX_FMTS` as 12, and declares helpers for instance state strings, cleanup/release, queue initialization, event subscription, output format get, format lookup by FourCC or index, V4L2-to-Wave standard mapping, returning queued buffers, updating multiplanar pixel formats, and IRQ kfifo allocation.

## Control Flow and Integration
Decoder and encoder open paths use `wave5_vpu_queue_init`, `wave5_kfifo_alloc`, and format helpers. Ioctl tables use `wave5_vpu_subscribe_event` and `wave5_vpu_g_fmt_out`. Release paths use `wave5_vpu_release_device` and `wave5_cleanup_instance`. The constants define fixed two-dimensional format arrays for codec and raw formats.

## State and Persistence
The header owns no state. It declares functions that operate on `struct vpu_instance`, `struct vpu_device`, vb2 queues, V4L2 file handles, and V4L2 pix formats owned elsewhere.

## Dependencies and Risks
The header depends on `wave5-vpu.h` for all core type definitions. `MAX_FMTS` is a coupling point: format arrays in frontend files must not exceed it, and lookup code treats zero FourCC entries as terminators.

## Test Signals
Compile decoder and encoder with this header, enumerate all format indices up to `MAX_FMTS`, exercise event subscriptions, and run open/release tests that prove the declarations match implementation signatures.
