# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.h

### Purpose
`dvb-pll.h` declares the public interface and descriptor IDs for the simple DVB PLL tuner helper implemented in `dvb-pll.c`.

### Important APIs, Types, And Functions
The header defines numeric `DVB_PLL_*` IDs from `DVB_PLL_UNDEFINED` through `DVB_PLL_TDA665X_EARTH_PT1`. `struct dvb_pll_config` carries the frontend pointer used by the I2C-client probe path. `dvb_pll_attach()` attaches a descriptor-selected PLL to a frontend, I2C address, and adapter.

### Control Flow
There is no runtime logic beyond Kconfig reachability. When `CONFIG_DVB_PLL` is reachable, callers link to the exported attach function. Otherwise the inline stub logs a warning and returns `NULL`.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux I2C and DVB frontend declarations and must stay synchronized with the descriptor array and I2C device table in `dvb-pll.c`.

### Integration Points
Board drivers use the constants to choose a tuner descriptor. I2C module loading uses `struct dvb_pll_config` as platform data for the I2C driver probe.

### Risks
The numeric ID ABI is order-sensitive: changing values without updating board users breaks descriptor selection. The stub returns `NULL`, so callers must handle disabled Kconfig builds.

### Test Signals
Build tests should cover reachable and disabled Kconfig cases, all descriptor IDs used by board files, and I2C-platform-data attach paths.
