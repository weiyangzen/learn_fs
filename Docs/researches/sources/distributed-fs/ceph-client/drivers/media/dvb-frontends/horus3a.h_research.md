# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.h

### Purpose
`horus3a.h` declares configuration and attach API for the Sony HORUS3A satellite tuner.

### Important APIs, Types, And Functions
`struct horus3a_config` contains the tuner I2C address, oscillator frequency in MHz, and optional parent callback context/function. `horus3a_attach()` attaches tuner ops to an existing frontend.

### Control Flow
Enabled Kconfig builds use the exported attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored in the header. Runtime state is allocated by `horus3a.c`. It depends on Linux DVB frontend and I2C types.

### Integration Points
Satellite board drivers pass this config when wiring HORUS3A behind a demodulator-controlled I2C gate.

### Risks
The attach comment incorrectly refers to `struct helene_config`, which can mislead users. Callers must use the address format expected by the implementation, which shifts `i2c_address` right by one.

### Test Signals
Build enabled/disabled Kconfig variants, attach with board configs, and validate callback invocation plus address handling.
