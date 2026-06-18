# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.c

## Purpose
`ivtv-i2c.c` provides ivtv's I2C adapter implementation and subdevice registration logic. It supports both a custom CX23415/16 bit-banging algorithm and the older `i2c-algo-bit` path, then probes/registers video decoders, audio codecs, tuners, EEPROM, ghost-reduction/YCS chips, GPIO pseudo-hardware, and IR receivers.

## Important APIs, Types, and Functions
Key exported functions are `init_ivtv_i2c()`, `exit_ivtv_i2c()`, `ivtv_i2c_register()`, `ivtv_find_hw()`, and `ivtv_i2c_new_ir_legacy()`. Internal logic includes `hw_addrs`, `hw_devicenames`, `get_key_adaptec()`, `ivtv_i2c_new_ir()`, custom I2C primitives `ivtv_start()`, `ivtv_stop()`, `ivtv_sendbyte()`, `ivtv_readbyte()`, `ivtv_write()`, `ivtv_read()`, `ivtv_xfer()`, and old bit-algo callbacks.

## Control Flow
Probe initializes the adapter with `init_ivtv_i2c()`, choosing the custom algorithm when `options.newi2c > 0`, setting clock timing, binding adapter data to the V4L2 device, setting SCL/SDA high, and registering the bus. `ivtv_load_and_init_modules()` iterates hardware bits and calls `ivtv_i2c_register()`, which handles tuners with board-specific address lists, IR receivers with platform init data, cx25840 with platform data, and other subdevices by fixed or scanned addresses. The custom transfer path serializes the bus with `i2c_bus_lock`, performs combined write-read without an intervening stop, retries operations up to eight times, and returns Linux I2C status.

## State and Persistence
State includes `itv->i2c_adap`, `itv->i2c_algo`, `itv->i2c_client`, `itv->i2c_state`, `itv->i2c_bus_lock`, subdev `grp_id` masks, and IR init data. Hardware line state is volatile. No persistent storage is written.

## Dependencies and Integration Points
The file depends on Linux I2C core, V4L2 I2C subdev helpers, card hardware bit definitions, GPIO reset support, cx25840 platform data, tuner address lists, and IR keymap/protocol helpers. Driver card detection, EEPROM reads, routing, controls, and firmware-adjacent subdev setup all depend on successful I2C registration.

## Risks and Edge Cases
`hw_addrs` and `hw_devicenames` must match `IVTV_HW_BIT_*` ordering. Address collisions are possible, especially legacy Hauppauge IR probing. The custom bus relies on polling MMIO line state and retries to recover stuck SCL/SDA. Combined transaction stop handling is required for chips such as msp3400. `ivtv_find_hw()` matches exact `grp_id`, so duplicate or missing group IDs break later routing.

## Test Signals
Validate both `newi2c` and old bit-algo modes, module parameter clock bounds, EEPROM reads, tuner probing with radio/demod/TV address lists, all declared subdevice `grp_id` values, IR registration and Adaptec key reads, combined write-read transactions, stuck bus recovery logs, and clean adapter deletion on probe failure/remove.
