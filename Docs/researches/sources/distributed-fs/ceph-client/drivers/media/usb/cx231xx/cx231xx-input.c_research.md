# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-input.c

Purpose: IR remote-control glue for cx231xx boards that use an external I2C IR microcontroller instead of the chip's internal IR block. It binds `ir-kbd-i2c` to the board-specified I2C adapter and supplies a cx231xx-specific key polling callback.

Important APIs/types/functions: `get_key_isdbt()` is the `IR_i2c` polling callback; it reads one byte from the I2C client, treats `0xff` as no key, bit-reverses other command bytes into scancodes, reports `RC_PROTO_OTHER`, and returns whether a key was found. `cx231xx_ir_init()` allocates an rc-core scancode device, fills `IR_i2c_init_data`, sets board keymap and NEC-related masks, and creates an `ir_video` I2C client at address `0x30`. `cx231xx_ir_exit()` unregisters the I2C client and clears the stored pointer.

Control flow: initialization first checks `cx231xx_boards[dev->model].rc_map_name`; boards without a keymap return `-ENODEV` and skip IR setup. It requests the `ir-kbd-i2c` module, zeroes board info and init data, allocates an `RC_DRIVER_SCANCODE` device, fills platform data, selects the board's `ir_i2c_master`, and calls `i2c_new_client_device(cx231xx_get_i2c_adap(...), &info)`. Once bound, `ir-kbd-i2c` calls `get_key_isdbt()` to poll the hardware. Exit unregisters the client.

State and persistence: persistent state is `dev->init_data`, the allocated `rc_dev` owned through the I2C IR client, and `dev->ir_i2c_client`. The external IR controller's last key state is read over I2C; no persistent configuration is stored on disk. Keymaps come from board data.

Dependencies and integration: depends on cx231xx board definitions, exported `cx231xx_get_i2c_adap()`, Linux I2C, rc-core, `ir-kbd-i2c`, and `bitrev8()`. It integrates with boards that define both `rc_map_name` and `ir_i2c_master`.

Risks: `cx231xx_ir_init()` does not check `i2c_new_client_device()` with `IS_ERR()`/NULL and still returns 0, so IR binding failure can look successful and leave cleanup paths with an invalid or null client. If `i2c_new_client_device()` fails after `rc_allocate_device()`, ownership/freeing of `dev->init_data.rc_dev` is not explicit in this file. `cx231xx_ir_exit()` calls `i2c_unregister_device()` unconditionally, so it relies on callers only invoking exit after successful init or on the helper tolerating NULL. The callback reports `RC_PROTO_OTHER` even though init data sets `RC_PROTO_BIT_NEC`, reflecting that the microcontroller emits only command bytes; keymap compatibility must be verified per board.

Test signals: probe a board with `rc_map_name` and verify `ir-kbd-i2c` autoload and client creation at address `0x30`; press/hold/release keys and confirm `0xff` no-key behavior, `0xfe` hold behavior, bit-reversed scancodes, and keymap matches; remove/unplug after failed and successful IR init; test missing `ir-kbd-i2c` module; validate `ir_i2c_master` points to a registered cx231xx adapter or mux adapter.
