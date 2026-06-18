# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb.c

## Purpose
Implements the DiBcom 3000M-B DVB-T COFDM demodulator frontend. It handles I2C register access, chip identification, frontend initialization, DVB-T parameter programming, optional autosearch, TPS readback, lock/statistic reads, sleep, PID filtering, FIFO control, and tuner I2C pass-through for legacy DiB bridge devices.

## Important APIs, Types, And Functions
The private `struct dib3000_state` is defined in `dib3000mb_priv.h` and stores the I2C adapter, copied config, frontend, timing state, and last tuned bandwidth/frequency fields. The C file's low-level accessors are `dib3000_read_reg()` and `dib3000_write_reg()`, wrapped by private-header macros such as `rd`, `wr`, and `wr_foreach()`.

The main frontend callbacks are `dib3000mb_fe_init_nonmobile()`, `dib3000mb_sleep()`, `dib3000mb_set_frontend_and_tuner()`, `dib3000mb_get_frontend()`, `dib3000mb_read_status()`, BER/strength/SNR/uncorrected-block readers, and `dib3000mb_release()`. `dib3000mb_attach()` verifies DiBcom vendor ID `0x01b3` and device ID `0x3000`, copies `dib3000mb_ops`, and fills `struct dib_fe_xfer_ops` with PID/FIFO/tuner-pass callbacks.

## Control Flow
Initialization powers up the demodulator, resets hardware, programs clock/electrical output, default DDS/timing/bandwidth values, impulse noise, AGC, phase-noise, lock masks, filter coefficients, mobile/multi-demod values, output/FIFO/MPEG2/PID defaults, and disables diversity input. Set-frontend first lets the tuner tune through `fe->ops.tuner_ops.set_params`, closes the I2C gate if present, programs bandwidth-specific timing/filter tables, then translates DVB property-cache transmission mode, guard, inversion, modulation, hierarchy, and FEC into demodulator registers.

For auto parameters, the driver computes an autosearch sequence index from auto FFT/guard/inversion flags, inhibits ISI, restarts autosearch, polls IRQ/lock status up to 100 ms, reads TPS values with `dib3000mb_get_frontend()` on success, and recursively reprograms without tuner retune. Otherwise it restarts the control path directly. Status and metrics read dedicated monitoring registers and translate lock bits into `FE_HAS_*` flags.

## State And Persistence
Most persistent behavior is in hardware registers. Driver heap state persists the config, frontend, I2C pointer, and unused/legacy timing fields. PID filter state is written into hardware PID registers beginning at `DIB3000MB_REG_FIRST_PID`; FIFO and PID parser state persist in the demodulator until changed. The implementation does not serialize I2C access with a local mutex.

## Dependencies And Integration Points
The file depends on Linux module/delay/slab APIs, DVB frontend APIs, `dib3000.h`, and the private register-map header. It integrates with an external tuner through frontend tuner ops and I2C gate control, and with bridge drivers through the `dib_fe_xfer_ops` callbacks for PID filtering, FIFO control, and tuner pass-through. It exports only `dib3000mb_attach()`.

## Risks
The driver relies heavily on magic register constants and batch tables; wrong values can silently degrade lock or transport output. I2C read failures return zero after debug logging, which can be confused with valid lock/status values. Recursive reprogramming after autosearch can re-enter large parts of set-frontend and needs the property cache to be coherent. The mapping for `DIB3000_FEC_5_6` in `get_frontend()` assigns `FEC_4_5`, which appears inconsistent with the debug text and other mappings. `xfer_ops` is written without a null check, and no local locking protects concurrent frontend callbacks.

## Test Signals
Build with `CONFIG_DVB_DIB3000MB` and exercise attach ID checks. Runtime tests should cover init, sleep, 6/7/8 MHz tuning, all-auto and fixed DVB-T parameters, TPS readback after autosearch, lock-bit progression, BER/strength/SNR/uncorrected-block reads, PID filter enable/disable, FIFO enable/disable, and tuner pass-through register behavior on bridge hardware.
