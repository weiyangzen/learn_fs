# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.h

### Purpose
`helene.h` exposes configuration and attach APIs for the Sony HELENE tuner driver.

### Important APIs, Types, And Functions
`enum helene_xtal` lists supported crystal frequencies. `struct helene_config` carries I2C address, legacy MHz crystal value, RF-switch callback context/function, crystal enum, and a frontend pointer for I2C-client platform data. `helene_attach()` attaches terrestrial/cable ops, and `helene_attach_s()` attaches satellite ops.

### Control Flow
Enabled builds link to real attach functions. Disabled builds provide warning stubs returning `NULL`.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux DVB frontend and I2C declarations. Runtime state is allocated by `helene.c` based on this config.

### Integration Points
Board drivers and I2C platform-data users configure tuner address, crystal selection, and RF-switch callback through this header.

### Risks
The documentation for `helene_config` includes both `xtal_freq_mhz` and `xtal`, but the implementation primarily uses `xtal`. Callers must provide a valid frontend in I2C-client platform data.

### Test Signals
Build with enabled/disabled Kconfig, attach both terrestrial and satellite variants, and validate every supported `helene_xtal` value.
