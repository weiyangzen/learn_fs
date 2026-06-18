# Research: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.c

Purpose: Analog V4L2 video/VBI device implementation for cx23885 Video A. It provides format negotiation, input/audio/tuner ioctls, buffer queueing, RISC DMA startup, interrupt completion, analog tuner sharing, and video/VBI/audio registration.

Important APIs/types/functions: exported functions include `cx23885_video_register()`, `cx23885_video_unregister()`, `cx23885_video_irq()`, `cx23885_video_wakeup()`, `cx23885_set_tvnorm()`, `cx23885_enum_input()`, `cx23885_get_input()`, `cx23885_set_input()`, `cx23885_set_frequency()`, `cx23885_flatiron_write()`, and `cx23885_flatiron_read()`. Internal vb2 callbacks build packed YUYV RISC buffers. V4L2 ioctl ops cover querycap, format, VBI format, std, input, audio input, tuner, frequency, events, and optional advanced-debug register access.

Control flow: registration initializes default NTSC YUYV 720-wide interlaced state, optionally creates analog tuner subdevices, programs norm/input/audio mux, initializes video and VBI vb2 queues, registers `/dev/video*` and `/dev/vbi*`, then registers ALSA audio. Streaming prepares a field-aware RISC buffer, chains buffers in `dev->vidq`, programs SRAM channel 1 and video-A DMA, and completes buffers on RISCI1. Input ioctls route video through the cx25840 subdevice, apply board GPIO quirks, and route audio through cx25840 and optional Flatiron ADC mux. Frequency ioctls either use V4L2 tuner subdev calls or DVB tuner ops via `analog_fe` on hybrid boards.

State and persistence: volatile state in `dev->tvnorm`, `fmt`, width/height/field, input, audinput, frequency, video/VBI queues, per-buffer RISC memory, registered `video_device` pointers, analog tuner subdevs, and audio device pointer. No on-disk persistence.

Dependencies/integration: V4L2 core/ioctls/events, vb2 DMA-SG, tuner and cx25840 subdev APIs, Flatiron I2C on internal bus, common RISC and IRQ helpers, `cx23885-vbi.c`, `cx23885-ioctl.c`, `cx23885-alsa.c`, board tables, and DVB-attached analog tuner sharing.

Risks: only YUYV is supported; format/norm changes are rejected while any video/VBI/MPEG queue is busy. Video and VBI share Video A DMA/interrupt registers. Hybrid-board analog frequency setup depends on DVB attachment populating `analog_fe`. Flatiron I2C reads/writes mostly log but do not propagate errors. Field order has board-specific `force_bff` behavior.

Test signals: video and VBI nodes register with correct caps; `v4l2-ctl --stream-mmap` captures stable YUYV; standard/input/audio/frequency ioctls update subdevices; tuner-capable hybrid boards tune analog via shared tuner; IRQ logs show no opcode/sync/fifo errors; unregister removes video, VBI, and ALSA devices.
