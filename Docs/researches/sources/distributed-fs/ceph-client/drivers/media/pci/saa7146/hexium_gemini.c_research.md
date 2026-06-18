# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/hexium_gemini.c

Purpose: V4L2/SAA7146 extension driver for Hexium Gemini frame grabber cards. It registers a PCI extension, configures SAA7146 port/DMA defaults, initializes a Samsung KS0127B decoder over I2C, exposes nine analog camera inputs, and delegates capture mechanics to `saa7146_vv`.

Important APIs, types, and functions: `struct hexium` stores the video device, I2C adapter, current input, current standard, and type. `hexium_ks0127b[]` is the decoder power-on register table. `hexium_pal`, `hexium_ntsc`, `hexium_secam`, and `hexium_input_select[]` encode standard/input writes. `hexium_init_done()`, `hexium_set_input()`, and `hexium_set_standard()` perform I2C programming. V4L2 entry points are `vidioc_enum_input()`, `vidioc_g_input()`, and `vidioc_s_input()`. Module flow uses `hexium_attach()`, `hexium_detach()`, `std_callback()`, `saa7146_register_extension()`, and `saa7146_unregister_extension()`.

Control flow: module init registers `hexium_extension`. On matching PCI subsystem IDs, attach allocates state, enables SAA7146 I2C pins, registers an I2C adapter, configures GPIO and DD1 stream registers, initializes the decoder table, sets PAL/input 0, initializes `saa7146_vv`, installs custom input ioctls into `vv_data.vid_ops`, and registers a video node. Standard changes from the shared vv layer call `std_callback()` to push KS0127B standard registers.

State and persistence: `cur_input` and `cur_std` are in-memory only. Decoder registers and SAA7146 registers retain hardware state until changed or reset. `hexium_num` tracks active devices for logging. No persistent storage is used.

Dependencies and integration points: depends on `saa7146_vv`, SAA7146 I2C helpers, Linux I2C SMBus transfer APIs, PCI matching, and V4L2 video-device registration. The `vv_data` structure links this board driver to common capture and standard handling.

Risks: I2C programming errors are often logged but not always fatal, so bad decoder state can lead to capture timeouts. Gemini Dual is explicitly not fully supported. `hexium_set_input()` assumes validated input indexes. Global `vv_data` is modified during attach, so this follows the legacy single-driver pattern rather than per-device immutable ops. Attach cleanup is mostly correct but depends on each failure path unwinding I2C/vv/device registration in order.

Test signals: build/load module, confirm PCI ID binding for subsystem `0x17c8:0x2401/0x2402`, enumerate nine inputs, switch each input while watching I2C errors, set PAL/NTSC/SECAM and validate frame geometry, stream from `/dev/video*`, and unload/reload while checking adapter and video-node cleanup.
