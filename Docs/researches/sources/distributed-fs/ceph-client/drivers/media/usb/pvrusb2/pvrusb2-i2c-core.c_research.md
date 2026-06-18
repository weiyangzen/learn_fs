# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.c

Purpose: implements the pvrusb2 I2C adapter by translating Linux I2C transfers into FX2 firmware commands and layering device-specific I2C quirks for IR receivers, wm8775, and cx25840 chips.

Important APIs, types, and functions: module parameters `i2c_scan`, per-unit `ir_mode`, and `disable_autoload_ir_video` shape initialization. `pvr2_i2c_write()`, `pvr2_i2c_read()`, and `pvr2_i2c_basic_op()` issue `FX2CMD_I2C_WRITE` and `FX2CMD_I2C_READ` through `pvr2_send_request()`. Special function entries include `i2c_24xxx_ir()`, `i2c_hack_wm8775()`, `i2c_black_hole()`, and `i2c_hack_cx25840()`. `pvr2_i2c_xfer()` is the adapter `master_xfer`, and `pvr2_i2c_functionality()` advertises `I2C_FUNC_SMBUS_EMUL | I2C_FUNC_I2C`. `pvr2_i2c_core_init()` and `pvr2_i2c_core_done()` are the public lifecycle hooks.

Control flow: initialization fills `hdw->i2c_func[]` with the basic operation, overrides specific addresses for disabled IR, emulated 24xxx IR, cx25840 wedge detection, or wm8775 probe success, configures `i2c_adapter`/`i2c_algorithm`, registers the adapter, optionally probes for newer IR hardware at `0x71`, optionally scans all addresses, and binds an IR I2C client. The transfer path chooses the function for the first address, supports one-message reads/writes and two-message write-then-read transactions, chunks reads to fit the shared 64-byte command buffer, rejects unsupported shapes, and logs traffic when enabled.

State and persistence: per-device state lives in `hdw->i2c_func[]`, `i2c_cx25840_hack_state`, `i2c_linked`, `ir_scheme_active`, and `ir_init_data`. I2C subdevice binding persists until `i2c_del_adapter()` in teardown. No disk state is written.

Dependencies and integration points: depends on `pvrusb2-hdw-internal.h`, FX2 command definitions, Linux I2C core, V4L2 subdevice discovery through the hardware core, and `ir-kbd-i2c` client data. `pvrusb2-hdw.c` initializes this before loading V4L2 submodules and calls teardown during disconnect.

Risks: only limited I2C transaction forms are supported; unsupported multi-message or address-changing transfers fail. The shared `cmd_buffer` limits transfer size and requires `ctl_lock` serialization. The cx25840 hack can deliberately disable address `0x44` and render the device useless if a wedged chip is detected. IR emulation fabricates data for legacy modules and can confuse probes if assumptions change.

Test signals: load with and without IR; run optional `i2c_scan`; verify tuner/decoder/audio subdevices attach; exercise IR on 29xxx, 24xxx, 24xxx MCE, and Zilog schemes; test long reads that require chunking; watch for unexpected I2C status logs, cx25840 wedge warnings, and correct adapter deletion on unplug.
