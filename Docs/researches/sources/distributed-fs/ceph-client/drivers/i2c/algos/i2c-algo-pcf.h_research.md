<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h

Purpose: local register-bit header for the PCF8584 algorithm implementation. It encodes control, status, clock, transmission-rate, and internal-register selection constants.

Important definitions: control bits include `I2C_PCF_PIN`, `ESO`, `ES1`, `ES2`, `ENI`, `STA`, `STO`, and `ACK`; compound commands include `I2C_PCF_START`, `STOP`, `REPSTART`, and `IDLE`. Status bits include initialization, bus error, last received bit, addressed-as-slave, lost arbitration, and bus busy. Clock and transfer constants define supported oscillator and serial rates.

Control flow and state: no functions. Its constants are consumed by `i2c-algo-pcf.c` to select PCF internal registers and interpret hardware state.

Dependencies and integration: private to the PCF algorithm, complementing public callback declarations in `linux/i2c-algo-pcf.h`.

Risks and tests: bit definition errors directly corrupt bus sequencing. Test indirectly through PCF8584 init, status polling, START/STOP/repeated-start transfers, LRB ACK detection, and LAB recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h -->
