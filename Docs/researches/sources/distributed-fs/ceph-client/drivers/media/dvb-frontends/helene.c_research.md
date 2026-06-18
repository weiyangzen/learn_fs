# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.c

### Purpose
`helene.c` is the Sony HELENE CXD2858ER tuner driver for satellite, terrestrial, cable, and ISDB systems. It programs tuner analog, PLL, AGC, IF/IQ output, and power-save registers based on frontend delivery system and bandwidth.

### Important APIs, Types, And Functions
`struct helene_priv` stores I2C address/adapter, active frequency in kHz, state, parent tuner-selection callback, and crystal enum. The file defines Sony TV-system enums, a terrestrial adjustment table, register I/O helpers, power-save helpers, `helene_get_tv_system()`, satellite and terrestrial tuning paths (`helene_set_params_s()` and `_t()`), shared `helene_set_params()`, and `helene_x_pon()` power-on initialization. Public entry points are `helene_attach()`, `helene_attach_s()`, and the I2C-driver `helene_probe()`.

### Control Flow
Attach allocates private state, opens the demod I2C gate, runs `helene_x_pon()`, closes the gate, installs tuner ops, and stores `fe->tuner_priv`. `helene_x_pon()` performs a large first-power-on sequence, boots the internal CPU, checks CPU status, calibrates VCO current, disables outputs, and enters standby. Tuning maps DVB/ISDB/cable/satellite properties to a Sony TV-system ID, switches board RF path through the optional callback, wakes power-save as needed, computes rounded frequency, selects table-driven gain/overload/filter offsets for terrestrial modes or symbol-rate-based LPF for satellite modes, then writes burst register blocks.

### State, Persistence, And Dependencies
State persists in `fe->tuner_priv` or devm-managed I2C-client data. `priv->state` prevents redundant power-save transitions, and `priv->frequency` backs `get_frequency()`. Hardware register settings persist until sleep or retune. Dependencies include I2C transfer APIs, optional frontend I2C gate control, parent RF-switch callback, DVB frontend property cache, and HELENE config values.

### Integration Points
Legacy board drivers can attach terrestrial-only or satellite-only tuner ops, while I2C-device users get combined Sat/Ter ops. The parent callback selects which RF path is active, making this driver part of multi-standard frontend stacks.

### Risks
Most register writes ignore return values, so partial I2C failures can still report success. `helene_probe()` uses devm allocation but installs a normal `release` callback that calls `kfree()` on `fe->tuner_priv`, creating a lifetime mismatch if the frontend releases devm memory. The terrestrial table is indexed by enum values and must remain aligned. Frequency units differ internally between satellite, terrestrial, and `get_frequency()`.

### Test Signals
Test legacy and I2C-client attach, CPU error handling in `helene_x_pon()`, all supported delivery-system/bandwidth mappings, RF-switch callback behavior, sleep/init transitions, I2C gate open/close, devm lifetime release, and tuned-frequency reporting.
