# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-empress.c

Purpose: implements the Empress MPEG encoder support module for SAA7134 boards that expose a hardware MPEG stream through the common TS DMA path. It registers an additional V4L2 MPEG capture node and bridges MPEG format ioctls to the encoder subdevice and existing analog controls.

Important APIs, types, and functions: `empress_nr[]` selects MPEG device numbers. `saa7134_empress_qops` wraps TS queue helpers, adding encoder-specific start/stop behavior. Format handlers advertise and configure only `V4L2_PIX_FMT_MPEG`. `ts_fops` and `ts_ioctl_ops` expose read, mmap, poll, vb2 buffer ioctls, tuner/input/std controls, and event subscription. `empress_init()` and `empress_fini()` are installed in `empress_ops` for core MPEG registration.

Control flow: loading the module calls `saa7134_ts_register(&empress_ops)`. For matching devices, `empress_init()` allocates a video device, combines selected analog controls with encoder-subdevice controls, initializes `dev->empress_vbq` with DMA-SG memory, registers the MPEG V4L2 node, and schedules a signal-status update. Streaming calls `saa7134_ts_start_streaming()`, sends a board-specific leading-null-byte setting to subdevices via `core.init`, unmutes I2S audio, and marks `dev->empress_started`. Stop calls `saa7134_ts_stop_streaming()`, toggles `SAA7134_SPECIAL_MODE` to reset the path, mutes audio, and clears the started flag.

State and persistence: maintains `dev->empress_dev`, `dev->empress_ctrl_handler`, `dev->empress_vbq`, `dev->empress_workqueue`, and `dev->empress_started`. It uses the shared `dev->ts_q` DMA queue and encoder subdevice state. No persistent storage is used.

Dependencies and integration points: depends on the core MPEG ops registry, common TS DMA helpers, vb2 DMA-SG, V4L2 controls/events/ioctls, analog tuner/input/std helpers from the base driver, the optional `saa6752hs` encoder subdevice created by core, and audio mute/I2S registers.

Risks: Empress shares TS resources with DVB/TS code, so queue and stop sequencing must leave channel 5 clean. USERPTR is deliberately excluded because SAA7134 DMA requires page-start-aligned buffers. Signal updates are currently diagnostic only. Resetting `SPECIAL_MODE` on stop may affect other active paths if board state assumptions are wrong.

Test signals: MPEG device node registration, `VIDIOC_ENUM_FMT` reporting MPEG only, buffer allocation/streamon/read/mmap, encoder subdevice control propagation, audio unmute/mute around streaming, signal-change work execution, module unload while idle and while previously streamed, and media topology updates after late module load.
