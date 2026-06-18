# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-driver.h

## Purpose
This is the central internal header for cx18. It defines driver constants, stream types, debug macros, buffer and MDL structures, VBI state, DVB state, I2C callback data, the main `struct cx18`, and cross-file prototypes/macros.

## Important APIs, Types, and Functions
Key constants include card IDs, stream type IDs, PCI IDs, default buffer counts and sizes, debug flags, stream flags, instance flags, VBI constants, and `CX18_MAX_MMIO_WR_RETRIES`. Key structures include `cx18_options`, `cx18_enc_idx_entry`, `cx18_vb2_buffer`, `cx18_buffer`, `cx18_mdl`, `cx18_queue`, `cx18_dvb`, `cx18_in_work_order`, `cx18_stream`, `cx18_open_id`, `vbi_info`, `cx18_i2c_algo_callback_data`, and `cx18`. Inline helpers are `file2id()`, `fh2id()`, `to_cx18()`, and `cx18_raw_vbi()`.

## Control Flow
The header contributes call macros `cx18_call_hw()`, `cx18_call_all()`, and their error-returning variants. These route V4L2 subdev calls by `grp_id`, enabling board-specific subdevices to be addressed by hardware flags.

## State and Persistence
`struct cx18` is the persistent in-memory device state for a PCI function. Per-stream queue state tracks free, busy, full, and idle MDLs; VBI state tracks capture geometry and MPEG insertion buffers; flags and atomics coordinate open, capture, firmware, radio, pause, and stop behavior.

## Dependencies and Integration Points
The header pulls in Linux PCI, interrupt, I2C, workqueue, mutex, V4L2, tuner, DVB, vb2, mailbox, A/V core, and cx23418 firmware API definitions. Nearly every cx18 implementation file depends on this contract.

## Risks and Edge Cases
Structure fields are shared across IRQ, workqueue, file, ioctl, DVB, and ALSA contexts; lock and flag discipline must be preserved. Buffer-size constants encode firmware alignment requirements for YUV and index streams. The debug macros assume a local `cx` or `dev` variable, which affects call-site naming.

## Test Signals
Broad compile coverage is essential. Runtime signals include no queue corruption under concurrent read/poll/stop, correct device state in `VIDIOC_LOG_STATUS`, sane buffer sizing from module options, and stable VBI and DVB data paths.
