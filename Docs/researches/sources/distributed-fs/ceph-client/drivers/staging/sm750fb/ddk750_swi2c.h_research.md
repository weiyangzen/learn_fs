## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.h

Purpose: this header exposes the software I2C helper API for the SM750 DDK layer and defines the default GPIO pins used for SCL and SDA.

Important APIs: `sm750_sw_i2c_init(clk_gpio, data_gpio)` initializes GPIO-backed bit-banged I2C; `sm750_sw_i2c_read_reg(addr, reg)` reads one register from an I2C slave; `sm750_sw_i2c_write_reg(addr, reg, data)` writes one slave register. `DEFAULT_I2C_SCL` and `DEFAULT_I2C_SDA` default to GPIO 30 and 31.

Control flow and state: the header does not store state, but its API controls static state in `ddk750_swi2c.c` for selected GPIO pins and register-bank offsets. Consumers call init before read/write; the implementation does not enforce that contract except through whatever values the static defaults currently hold.

Dependencies and integration points: included by `ddk750_swi2c.c` and indirectly used from SM750 hardware initialization. It is part of the staging framebuffer driver's private DDK interface rather than Linux's I2C subsystem.

Risks: the default GPIO definitions are duplicated in `ddk750_reg.h`, and the API takes raw 8-bit addresses/registers without documenting whether `addr` is a shifted 8-bit address or a 7-bit address. The header exposes no locking or adapter object, so concurrent users would share a single implicit bus configuration.

Test signals: build coverage is enough for syntax; behavioral signals come from `ddk750_swi2c.c` tests, especially verifying that callers use shifted addresses consistently and call initialization with valid pins before transfers.
