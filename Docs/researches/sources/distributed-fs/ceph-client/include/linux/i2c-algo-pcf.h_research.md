# sources/distributed-fs/ceph-client/include/linux/i2c-algo-pcf.h

## Purpose
Defines the PCF8584 I2C adapter algorithm interface.

## APIs, Control Flow, and State
`struct i2c_algo_pcf_data` carries private data plus callbacks to set/get PCF controls, get own address and clock, wait for pin/interrupt, and optional transfer begin/end hooks. `lab_mdelay` controls multi-master lost-arbitration backoff. `i2c_pcf_add_bus()` attaches the algorithm. State lives in adapter `algo_data`, hardware control/status registers, and the configured arbitration delay.

## Dependencies, Integration, Risks, and Tests
Depends on I2C adapter definitions from surrounding includes. Integrates with board drivers for PCF8584-like hardware. Risks include missing multi-master backoff, callbacks that do not serialize hardware access, incorrect own-address/clock reporting, and wait callbacks that hang indefinitely. Test signals include transfer tests, arbitration-loss injection, bus clock verification, and timeout behavior during missing interrupts.
