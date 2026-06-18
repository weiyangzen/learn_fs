# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/mxb.c

Purpose: V4L2/SAA7146 extension driver for the Siemens-Nixdorf Multimedia eXtension Board. It coordinates SAA7146 video/VBI capture with multiple I2C subdevices for video decoding, tuner control, audio demodulation, and audio crosspoint routing.

Important APIs, types, and functions: `struct mxb` stores video/VBI devices, I2C adapter, subdev pointers, current input/audio/mute/frequency/mode. Static tables define four video inputs, six audio inputs, video-to-audio mapping, TEA6420 routing, SAA7146 port selections, and SAA7146 standards. `mxb_probe()` creates the I2C adapter and required subdevices. `mxb_init_done()` mutes audio, initializes tuner/video decoder/audio mode, optional SAA7740 sound module, and SAA7146 port registers. V4L2 handlers implement input, tuner, frequency, audio, querystd, and advanced register debug. `std_callback()` pushes standard changes to SAA7111A, tuner, and GPIO.

Control flow: module init registers an SAA7146 extension with I2C IRQ usage. Attach initializes `saa7146_vv`, probes all MXB I2C devices, installs video and VBI ioctl hooks, registers the video device, optionally registers VBI for nonzero SAA7146 revisions, logs the board, and runs board initialization. Input switching changes SAA7146 HPS source/sync, routes the TEA6415C crosspoint where needed, selects the SAA7111A input, updates allowed norms, and routes audio if unmuted. Frequency and tuner ioctls call into tuner/audio subdevices.

State and persistence: current input, audio source, mute state, tuner mode, and clamped frequency are kept in `struct mxb`. Module parameter `freq` supplies initial tuning. Hardware state persists only in volatile SAA7146 and I2C subdevice registers. `mxb_num` counts attached boards.

Dependencies and integration points: depends on `saa7146_vv`, `tuner`, `saa7111`, `tda9840`, `tea6415c`, `tea6420`, V4L2 subdev calls, I2C transfer APIs, and SAA7146 device registration. The Kconfig autoselects the needed media I2C drivers when enabled.

Risks: all required subdevices must be present or probe aborts. The optional SAA7740 initialization disables fast I2C IRQ mode globally in `extension.flags`, which affects later behavior. Error unwinding in attach can leak probe-created I2C state on some registration failures. Audio routing tables are index-sensitive. VBI availability depends on SAA7146 revision. Advanced register debug can directly alter device registers.

Test signals: load with helper subdrivers present; confirm video and, on revision >0, VBI node registration; enumerate four inputs and six audio sources; switch each video/audio input and verify crosspoint routing; tune frequency and read back clamped value; set PAL-BG/PAL-I/NTSC/SECAM; stream video and VBI; test mute control; inspect dmesg for missing I2C devices and SAA7740 detection.
