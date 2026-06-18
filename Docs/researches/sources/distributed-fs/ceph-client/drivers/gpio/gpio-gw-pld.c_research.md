
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-gw-pld.c

Purpose: supports Gateworks I2C PLD GPIO expanders with a simple open-drain 8-bit register model.

Important APIs/types/functions: `struct gw_pld` stores gpiochip, I2C client, and `out` shadow byte. GPIO callbacks are `gw_pld_input8()`, `gw_pld_get8()`, `gw_pld_output8()`, `gw_pld_set8()`, and `gw_pld_probe()`.

Control flow: probe allocates state, initializes an 8-line can-sleep gpiochip, sets the I2C client, enables `I2C_M_IGNORE_NAK` because the PLD does not reliably acknowledge, initializes `out` to `0xff`, stores client data, and registers the gpiochip. Direction input sets the corresponding output-shadow bit to one and writes the byte; output updates the shadow bit according to requested value and writes it. Get reads one byte and returns the target bit.

State and persistence behavior: `out` is the only software state and shadows the last written open-drain output byte. Hardware state persists in the PLD register. There is no IRQ, PM, locking, or regmap cache.

Dependencies and integration points: depends on I2C SMBus byte operations, gpiolib, I2C id `gw-pld`, and OF compatible `gateworks,pld-gpio`.

Risks: reads returning an I2C error are converted to GPIO value 0 instead of propagating the error. No lock protects `out`, so concurrent set/direction calls can lose updates. Ignoring NAK is necessary for hardware but can hide bus problems.

Test signals: probe with OF/I2C IDs, open-drain input-as-one behavior, output shadow writes, readback through SMBus byte, I2C error handling behavior, and concurrent GPIO set stress.
