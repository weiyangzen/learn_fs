# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.c

### Purpose
`dvb-pll.c` is the shared simple PLL tuner implementation for legacy DVB frontends. It provides descriptor-driven programming for many Thomson, LG, Infineon, Philips, Alps, Samsung, Panasonic, Opera, Friio, and EarthSoft tuner variants, then exposes them through `dvb_tuner_ops` and an optional I2C driver binding.

### Important APIs, Types, And Functions
`struct dvb_pll_desc` describes each tuner: name, frequency range, IF offset, optional init/sleep data, optional `set()` adjustment hook, and limit/step/config/cb table entries. `struct dvb_pll_priv` stores the chosen descriptor, I2C adapter/address, an IDA slot, and cached tuned frequency/bandwidth. `dvb_pll_attach()` is the legacy exported attach API. `dvb_pll_configure()` computes the PLL divisor and four-byte payload. Tuner callbacks include `dvb_pll_init()`, `dvb_pll_sleep()`, `dvb_pll_set_params()`, `dvb_pll_calc_regs()`, and frequency/bandwidth getters.

### Control Flow
Attach allocates a temporary probe byte and IDA number, optionally overrides the requested descriptor through the debug `id[]` module parameter, probes the I2C address when an adapter is provided, allocates private state, installs tuner ops, fills tuner info, and suppresses init/sleep callbacks when no descriptor data exists. Set-params selects the first descriptor entry whose limit covers the requested frequency, computes `(frequency + iffreq + stepsize / 2) / stepsize`, lets descriptor-specific hooks adjust bandwidth or special writes, sends the four bytes over I2C through an opened frontend gate, and caches the actual programmed frequency.

### State, Persistence, And Dependencies
Persistent driver state is in `fe->tuner_priv`; the IDA slot tracks debug override slots and is freed by the I2C remove path, but the legacy release path only frees private data. Hardware state persists in tuner registers written over I2C. Dependencies include `dvb_frontend`, `i2c_transfer`, optional `fe->ops.i2c_gate_ctrl`, IDA, module parameters, and Kconfig reachability through `dvb-pll.h`.

### Integration Points
Boards can call `dvb_pll_attach()` directly or instantiate the `dvb_pll` I2C driver with `struct dvb_pll_config` platform data. The attach path populates `fe->ops.tuner_ops`, while the I2C probe clears `tuner_ops.release` to avoid double module release when `dvb_module_release()` also owns lifetime.

### Risks
`BUG_ON()` rejects invalid descriptor IDs and can crash if callers pass bad IDs. Legacy attach does not free the IDA slot in `dvb_pll_release()`, while I2C remove does. Descriptor tables encode many hardware-specific magic values and several hooks perform immediate I2C writes before final buffer edits. I2C gate close is inconsistent after some writes. The debug `id[]` override can force incompatible descriptors.

### Test Signals
Useful tests are attach/probe failure paths, per-descriptor frequency boundary tuning, 6/7/8 MHz bandwidth-specific hooks, init/sleep data writes, `calc_regs()` buffer sizing, no-I2C attach behavior, I2C-driver remove lifetime, and forced `id[]` descriptor overrides.
