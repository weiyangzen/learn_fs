## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.c

Purpose: this file implements a bit-banged I2C master over SM750 GPIO pins. It is used during SM750LE hardware initialization to configure an external DVI transmitter such as CH7301 when present.

Important APIs and functions: exported-to-driver functions are `sm750_sw_i2c_init()`, `sm750_sw_i2c_read_reg()`, and `sm750_sw_i2c_write_reg()`. Internal helpers are `sw_i2c_wait()`, `sw_i2c_scl()`, `sw_i2c_sda()`, `sw_i2c_read_sda()`, `sw_i2c_start()`, `sw_i2c_stop()`, `sw_i2c_write_byte()`, `sw_i2c_read_byte()`, `sw_i2c_ack()`, and the SM750LE-specific `sm750le_i2c_init()`.

Control flow: initialization validates GPIO numbers, chooses normal SM750 GPIO mux/data/direction registers or SM750LE data/direction registers, configures the pins as GPIO, enables GPIO power for non-LE chips, then sends repeated stop sequences to clear the bus. Write transfers issue start, device address, register index, data, and stop; each byte waits for an ACK by releasing SDA, clocking SCL, and polling SDA low with a retry loop. Read transfers write the target register index, issue a repeated start, send the read address, read one byte, and stop.

State and persistence: GPIO pin numbers and register offsets are module-global static variables. The bus electrical state persists in hardware GPIO direction/data registers, using open-drain behavior by driving low for zero and switching to input for high. No Linux I2C adapter is registered, so there is no bus locking outside this file.

Dependencies and integration points: depends on `ddk750_chip.h` for `peek32()`/`poke32()` and chip type, `ddk750_reg.h` for GPIO register definitions, `ddk750_power.h` for `sm750_enable_gpio()`, and `ddk750_swi2c.h` for public prototypes. `hw_sm750_inithw()` initializes GPIO 0/1 on SM750LE and probes/writes CH7301 registers through this API.

Risks: `sw_i2c_read_sda()` uses a suspicious comparison `(gpio_dir & dir_mask) != ~dir_mask`, which is effectively always true for normal masks and forces input each read; behavior works as a release operation but the condition is misleading. `sw_i2c_ack()` is a no-op, so multi-byte reads would not send real ACK/NACK sequencing. There is no external locking around global pin state or transfers. Timing is a CPU loop rather than calibrated delays. Read operations ignore ACK failures from address/register writes, returning whatever byte is sampled.

Test signals: CH7301 detection and configuration on SM750LE hardware is the primary runtime signal. Additional tests should include bus analyzer traces for start/stop/ACK timing, forced no-ACK behavior, probe across normal SM750 and SM750LE register sets, and suspend/resume validation because comments mention earlier timing/read problems after resume.
