# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-icy.c

Purpose: Amiga Zorro ICY card I2C driver for a PCF8584-style adapter. It uses `i2c-algo-pcf` in polling mode and auto-instantiates an LTC2990 sensor on known community board addresses.

Important APIs/types/functions: `struct icy_i2c` stores adapter, PCF register pointers S0/S1, and optional LTC2990 client. PCF callbacks are `icy_pcf_setpcf()`, `icy_pcf_getpcf()`, `icy_pcf_getown()`, `icy_pcf_getclock()`, and `icy_pcf_waitforpin()`. Probe/remove are `icy_probe()` and `icy_remove()` under a Zorro driver.

Control flow: probe allocates adapter and PCF algo data, reserves the four-byte Zorro resource, maps S0 at base and S1 at base+2, fills PCF callbacks, calls `i2c_pcf_add_bus()`, logs that IRQ is not implemented, and scans for an LTC2990 at 0x4c-0x4f with a software node describing measurement mode. Remove unregisters the optional client and deletes the adapter.

State and persistence: state is the Zorro MMIO pointers, adapter/algorithm data, and the created LTC2990 client pointer. PCF own address and clock values are fixed callback constants. No IRQ state is maintained.

Dependencies and integration: depends on Amiga/Zorro APIs, `z_readb/z_writeb`, `i2c-algo-pcf`, software nodes/properties for the LTC2990, and Zorro ID `VMC,15,0`.

Risks: IRQ support is intentionally absent because level-triggered Zorro interrupts do not fit `i2c-algo-pcf` expectations and could storm. The automatic sensor scan may instantiate only one matching client and assumes board conventions. The driver reaches into `../algos/i2c-algo-pcf.h`, coupling it to internal algorithm details.

Test signals: Zorro probe, PCF register read/write callbacks, polling I2C transfers, correct adapter naming, LTC2990 auto-detection and property exposure, and remove cleanup of both client and adapter.
