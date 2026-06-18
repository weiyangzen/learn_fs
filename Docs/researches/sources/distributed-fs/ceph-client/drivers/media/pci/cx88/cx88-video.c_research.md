# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-video.c

## Purpose
`cx88-video.c` is the main V4L2 analog video/radio driver for cx2388x function #0. It registers video, VBI, and optional radio devices; manages capture formats, controls, input muxing, tuner frequency, videobuf2 capture queues, video interrupts, power management, and helper subdevice setup.

## Important APIs, Types, And Functions
Public functions include `cx88_video_mux()`, `cx88_querycap()`, `cx88_enum_input()`, and `cx88_set_freq()`. Capture internals include `formats[]`, `format_by_fourcc()`, `start_video_dma()`, `stop_video_dma()`, `restart_video_queue()`, vb2 ops, `cx8800_vid_irq()`, and `cx8800_irq()`. V4L2 ioctl handlers cover video format, standards, inputs, tuner, frequency, debug registers, and radio. Probe/remove and PM are `cx8800_initdev()`, `cx8800_finidev()`, `cx8800_suspend()`, and `cx8800_resume()`.

## Control Flow
Probe allocates `cx8800_dev`, enables PCI/DMA, gets the shared core, requests the shared IRQ, builds audio/video controls, attaches helper modules as needed, sets default BGR24 format, stores `core->v4ldev`, initializes NTSC and input 0 under `core->lock`, creates vb2 queues, registers video/VBI/radio devices, and starts the TV-audio kthread for tuner boards. Video streaming prepares RISC buffers according to field layout, chains active buffers, programs SRAM channel 21, applies scaler and color format, enables capture/interrupt bits, and wakes buffers from RISC1 interrupts. Input changes update GPIOs, mux bits, S-video filter/AFE bits, external WM8775 routing, and I2S ADC mode for baseband audio. Frequency changes notify tuner subdevices, cache returned frequency, wait briefly, and reset TV audio.

## State, Persistence, And Dependencies
State is shared between `cx8800_dev` and `cx88_core`: current format, width/height/field, input, tuner frequency, control handlers, video/VBI queues, IRQ masks, WM8775/RTC subdevices, kthread, and active RISC buffers. There is no disk persistence. Dependencies include V4L2 core/ioctls/events, videobuf2 DMA-SG, PCI DMA, cx88 core/SRAM/RISC helpers, tuner and audio subdevices, and constants from `cx88-reg.h`.

## Integration Points
The file coordinates with `cx88-vbi.c` for VBI qops, `cx88-tvaudio.c` for audio setup, `cx88-input.c` for IR suspend/remove behavior, `cx88-mpeg.c` through `core->dvbdev` busy checks, and board metadata from `cx88-cards.c`. Userspace interacts through `/dev/video*`, `/dev/vbi*`, and optional `/dev/radio*`.

## Risks
Shared registers and interrupt masks make video/VBI concurrency delicate. Format changes reject busy video, VBI, and MPEG queues, but input/frequency changes still affect shared analog state. Buffer chaining patches DMA RISC jump addresses in active buffers and must be protected by queue lock expectations. Remove/suspend ordering must stop kthread, IR, DMA, IRQs, and device registration without use-after-free. Some probe failures after `core` acquisition must clear `core->v4ldev`.

## Test Signals
Run V4L2 compliance, video capture in every advertised pixel format and field mode, standard changes, input switching, tuner/radio open/frequency operations, control writes including WM8775 propagation, streamoff error cleanup, IRQ error injection if possible, suspend/resume with active video/VBI, and concurrent DVB busy checks.
