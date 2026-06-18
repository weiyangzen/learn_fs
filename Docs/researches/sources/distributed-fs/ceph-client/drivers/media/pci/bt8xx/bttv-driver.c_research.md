# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-driver.c

## Purpose
`bttv-driver.c` is the main V4L2 PCI driver for Brooktree/Conexant Bt848/Bt849/Bt878/Bt879 frame grabber chips. It owns module parameters, PCI probe/remove, chip initialization, V4L2 video/radio/VBI device registration, video buffer queues, analog input/audio routing, crop/standard management, IRQ handling, suspend/resume, and DVB subdevice autoload for cards with a digital transport path.

## Important APIs, Types, And Functions
The file exports global driver state `bttv_num`, `bttvs[]`, `bttv_debug`, `bttv_verbose`, and `bttv_gpio`. Probe entry is `bttv_probe()`, removal is `bttv_remove()`, module setup is `bttv_init_module()`, and PCI registration is via `bttv_pci_driver`. The main V4L2 surface is `bttv_video_template` with `bttv_fops` and `bttv_ioctl_ops`; radio uses `radio_template`, `radio_fops`, and `radio_ioctl_ops`. Buffer lifecycle hooks are `queue_setup()`, `buf_prepare()`, `buf_queue()`, `start_streaming()`, and `stop_streaming()`. Format and geometry ioctls include `bttv_try_fmt_vid_cap()`, `bttv_s_fmt_vid_cap()`, `bttv_g_selection()`, and `bttv_s_selection()`. The chip-control path includes `set_tvnorm()`, `set_input()`, `video_mux()`, `audio_input()`, `audio_mute()`, `set_pll()`, `bt848A_set_timing()`, `init_irqreg()`, and `init_bt848()`.

## Control Flow
Module initialization clamps capture-buffer parameters, checks PCI chipset quirks, registers the custom `bttv-sub` bus, then registers the PCI driver. `bttv_probe()` allocates and initializes `struct bttv`, enables PCI/MMIO/DMA, registers the V4L2 device, creates controls, identifies the board, requests the shared IRQ, initializes RISC/DMA and GPIO, runs card-specific initialization, registers I2C and tuner/audio subdevices, registers video/VBI/radio nodes, adds a DVB subdevice for boards with `has_dvb`, and optionally starts IR support. Runtime capture flows from V4L2 queue setup through `bttv_buffer_risc()` in `bttv-risc.c`; queued buffers cause DMA to start when the queue was empty. RISCI interrupts switch active video/VBI RISC hooks, complete old buffers, and advance sequence/timestamps. Timeout recovery tears down active DMA and marks outstanding buffers done/error.

## State And Persistence
Persistent in-memory state lives in `struct bttv`: current norm/input/frequency, controls, crop defaults/current crop, video/VBI resource ownership, active and queued buffers, IRQ counters, radio state, GPIO state, I2C state, and suspend snapshot. Hardware state is mirrored into Bt848 registers through `btwrite()` and recovered after reset/resume by `bttv_reinit_bt848()`. There is no disk persistence; module parameters and device state are reset on module unload or reprobe.

## Dependencies And Integration Points
This file integrates with PCI, V4L2 core, videobuf2 DMA-SG, media controller subdev calls, I2C subdevices, tuner/audio chips, rc-core IR support, and companion bttv files. It calls card tables from `bttv-cards.c`, RISC routines from `bttv-risc.c`, VBI routines from `bttv-vbi.c`, I2C setup from `bttv-i2c.c`, GPIO helpers from `bttv-gpio.c`, and input helpers from `bttv-input.c`. DVB support is triggered through `bttv_sub_add_device(&btv->c, "dvb")` and async `request_module("dvb-bt8xx")`.

## Risks
High-risk areas are IRQ/DMA races under `s_lock`, line ownership between VBI and video crop windows, hardware register programming during active capture, and legacy compatibility paths that intentionally permit overlap-like VBI settings while hardware truncates capture. `bttv_irq()` disables interrupt masks on lockup, so regressions can silently stop capture. Probe error paths have many resources to unwind; missed cleanup would leak IRQ/MMIO/V4L2 state. Format and crop calculations rely on chip limits and field semantics; off-by-one errors can corrupt DMA programs or reject valid userspace requests.

## Test Signals
Useful signals are successful PCI probe logs, registered `/dev/video*`, `/dev/vbi*`, and optional `/dev/radio*` nodes, `VIDIOC_QUERYCAP`, format negotiation across packed/planar/raw formats, VBI and video concurrent-stream rejection/acceptance according to line windows, radio tuner frequency operations, suspend/resume with active queues, IRQ counters without lockup messages, and successful buffer completion under `v4l2-compliance`, `qv4l2`, or capture tools.
