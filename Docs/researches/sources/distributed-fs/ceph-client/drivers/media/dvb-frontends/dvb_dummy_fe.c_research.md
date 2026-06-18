# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.c

### Purpose
`dvb_dummy_fe.c` implements synthetic DVB-T, DVB-C, and DVB-S frontend instances for bridge drivers or test configurations that need a frontend object without real demodulator hardware.

### Important APIs, Types, And Functions
`struct dvb_dummy_fe_state` only embeds a `dvb_frontend`. The exported attach functions are `dvb_dummy_fe_ofdm_attach()`, `dvb_dummy_fe_qpsk_attach()`, and `dvb_dummy_fe_qam_attach()`. Shared callbacks report a permanent lock, zero BER/SNR/strength/uncorrected blocks, no-op init/sleep/tone/voltage, and a set-frontend path that delegates tuner programming when present.

### Control Flow
Each attach function allocates state, copies a static `dvb_frontend_ops` template for OFDM, QPSK, or QAM, sets `demodulator_priv`, and returns the embedded frontend. `set_frontend()` calls `fe->ops.tuner_ops.set_params()` if installed and then closes the I2C gate when available. `read_status()` always sets all lock bits.

### State, Persistence, And Dependencies
State is memory-only and has no hardware persistence. The frontend operation templates encode delivery systems, ranges, symbol-rate limits, and capability flags. The module depends on DVB core structures and any attached tuner operations supplied by a parent driver.

### Integration Points
The module exports all three attach symbols for users needing dummy frontend registration. DVB-S dummy instances also provide SEC tone and voltage callbacks so satellite control calls do not fail.

### Risks
Because lock and quality metrics are fabricated, this driver can mask tuner, transport, or bridge failures if used outside intended dummy/test contexts. `get_frontend()` returns success without populating properties, and set-frontend ignores tuner errors.

### Test Signals
Test with frontend registration/unregistration, each delivery-system ops table, tuner delegation with I2C gate close, disabled Kconfig stubs, and userspace scans that expect permanent lock with zero metrics.
