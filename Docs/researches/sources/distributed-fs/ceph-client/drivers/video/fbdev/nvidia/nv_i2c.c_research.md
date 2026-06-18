# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_i2c.c

## Purpose

`nv_i2c.c` provides bit-banged I2C/DDC buses for `nvidiafb`, allowing EDID reads from NVIDIA display connectors through CRTC GPIO registers. The source was read as a complete 171-line file.

## Important APIs, Types, and Functions

Exported functions are `nvidia_create_i2c_busses()`, `nvidia_delete_i2c_busses()`, and `nvidia_probe_i2c_connector()`. Internal GPIO callbacks are `nvidia_gpio_setscl()`, `nvidia_gpio_setsda()`, `nvidia_gpio_getscl()`, and `nvidia_gpio_getsda()`. `nvidia_setup_i2c_bus()` configures `struct i2c_adapter` and `struct i2c_algo_bit_data` inside `struct nvidia_i2c_chan`.

## Control Flow

During common setup, `nvidia_create_i2c_busses()` initializes three channels. Connector bus order uses CRTC DDC bases `0x3e` and `0x36`, optionally reversed by `reverse_i2c`, plus a third bus at `0x50`. Each channel raises SDA/SCL, waits briefly, and registers with `i2c_bit_add_bus()`. EDID probing uses `fb_ddc_read()` on `chan[conn - 1]`; for connector 1 it falls back to firmware EDID if bit-bang DDC fails. Delete removes registered adapters and clears `chan[i].par`.

## State and Persistence Behavior

State lives in `par->chan[3]`, including adapter objects, DDC base offsets, and back-pointers to `par`. The driver does not persist EDID data; `nvidia_probe_i2c_connector()` returns a newly allocated EDID buffer to the caller, which later frees it.

## Dependencies and Integration Points

The file depends on the I2C bit-banging framework, fbdev EDID helpers, NVIDIA CRTC register accessors from `nv_setup.c`, and `../edid.h`. It is compiled only under `CONFIG_FB_NVIDIA_I2C`; otherwise `nv_proto.h` supplies no-op/probe-failure stubs. `NVCommonSetup()` consumes these probes to populate monitor specs and choose flat panel/CRT routing.

## Risks and Edge Cases

DDC GPIO register bit meanings are hard-coded. Wrong `reverse_i2c` configuration can attach monitor detection to the wrong connector. `nvidia_setup_i2c_bus()` clears `chan->par` on registration failure, so later delete/probe must honor that guard. Timeouts are short (`msecs_to_jiffies(2)`) and can miss slow DDC devices. The `conn` argument is used as `conn - 1`; callers must pass valid 1-based connector numbers.

## Test Signals

Build-test with `CONFIG_FB_NVIDIA_I2C`, verify three adapters register or cleanly fail, read EDID on connector 1 and 2, exercise `reverse_i2c`, confirm firmware EDID fallback for connector 1, and run probe/remove repeatedly to catch adapter cleanup issues.
