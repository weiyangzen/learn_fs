# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.c

### Purpose
`horus3a.c` implements a Sony HORUS3A DVB-S/S2 satellite tuner. It programs PLL divider, gain, LPF cutoff, calibration, IQ generator, and power-save state over I2C.

### Important APIs, Types, And Functions
`struct horus3a_priv` stores frequency, I2C address/adapter, sleep/active state, and an optional parent RF-selection callback. Helpers include bounded register writes, power-save enter/leave, `horus3a_set_params()`, frequency getter, and `horus3a_attach()`.

### Control Flow
Attach allocates state, normalizes the 8-bit address by shifting right, opens the demod I2C gate, waits after power-on, disables IQ generation, programs reference divider from `xtal_freq_mhz`, selects oscillator tuning value for 27/24/16 MHz crystals, enters power save, closes the gate, and installs tuner ops. Tuning calls the parent callback, leaves power save, rounds frequency to MHz, computes mixer divider and PLL `ms`, chooses F/G control bands from frequency ranges, computes LPF cutoff from DVB-S or DVB-S2 symbol rate formulas, writes registers `0x00` through `0x04`, gain/filter registers, starts calibration, enables IQ generation, waits 60 ms, and caches actual frequency.

### State, Persistence, And Dependencies
State lives in `fe->tuner_priv`; hardware state persists in tuner registers. `priv->state` avoids duplicate power-save writes. Dependencies include I2C transfer, sleep delays, optional I2C gate control, parent tuner callback, and DVB property cache delivery system/symbol rate/frequency.

### Integration Points
The driver fills `fe->ops.tuner_ops` for a satellite demodulator. Parent hardware can switch active tuner paths using `set_tuner_callback`.

### Risks
Most register write results are ignored, so retune may report success after I2C failure. Invalid crystal values only warn and continue with zeroed tuning value. The attach function does not verify chip identity. Delivery systems other than DVB-S/S2 return `-EINVAL`.

### Test Signals
Test attach with 16/24/27 MHz crystals, power-save transitions, DVB-S and DVB-S2 LPF calculations, boundary frequencies for gain/mixer ranges, parent callback behavior, I2C gate sequencing, and I2C error injection.
