# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-common.c

Purpose: shared low-level support for the TDA18271 analog/digital tuner: I2C gate selection, register read/write, default register initialization, standby programming, PLL calculation helpers, map-derived bitfield calculation, and debug printing.

Important APIs and functions: exported-to-module functions include `tda18271_read_regs`, `tda18271_read_extended`, `tda18271_write_regs`, `tda18271_init_regs`, `tda18271_charge_pump_source`, `tda18271_set_standby_mode`, `tda18271_calc_main_pll`, `tda18271_calc_cal_pll`, filter/map calculators, and `_tda_printk`. `__tda18271_write_regs` performs chunked writes and optional I2C bus locking.

Control flow: read helpers open the selected analog/digital gate, perform register reads, update the private register image, and preserve write-only extended bytes. Writes chunk the private register image according to `small_i2c`, optionally lock the I2C segment across multi-chunk operations, and close the gate. `tda18271_init_regs` writes a C1/C2-specific full register image, performs AGC setup, image rejection calibration for low/mid/high bands, synchronizes, and releases the bus. Calculation helpers look up PLL/filter values through maps and mutate the private register image without immediately writing every field.

State and persistence: all state lives in `struct tda18271_priv`: a 39-byte register shadow, selected gate/mode/role/version, output options, map layout, calibration state, and locks. Hardware state is synchronized from this shadow via explicit write calls.

Dependencies and integration points: depends on `tda18271-priv.h`, Linux I2C locking/transfer APIs, and frontend analog/digital I2C gate callbacks. It is used by `tda18271-fe.c` for init, calibration, tune, and standby.

Risks: `BUG_ON` is used for invalid write ranges, turning programming errors into kernel crashes. Many writes ignore return values during long calibration sequences. Gate selection depends on current mode when configured as auto; wrong mode can route I2C through the wrong demod bridge. Chunked writes and direct `__i2c_transfer` require careful bus locking.

Test signals: register trace comparison for C1 and C2 initialization, small-I2C chunk modes, analog vs digital I2C gate routing, read-extended write-only preservation, standby mode bit combinations, and map/PLL calculations over RF boundaries.
