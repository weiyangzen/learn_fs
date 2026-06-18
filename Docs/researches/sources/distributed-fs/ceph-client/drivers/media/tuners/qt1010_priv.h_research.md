# sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010_priv.h

## Purpose
`qt1010_priv.h` holds private constants, reverse-engineered register notes, operation codes, and private state declarations for the QT1010 driver. It is not a board-facing API.

## Important APIs and types
The header documents the apparent meaning of registers `0x00` through `0x2f`, including known frequency-scale registers and operation/measurement registers. It defines `QT1010_STEP` as 125 kHz, `QT1010_MIN_FREQ` as 48 MHz, `QT1010_MAX_FREQ` as 860 MHz, and `QT1010_OFFSET` as 1246 MHz. Operation constants are `QT1010_WR`, `QT1010_RD`, and `QT1010_M1`. `qt1010_i2c_oper_t` stores one scripted operation as `{ oper, reg, val }`. `struct qt1010_priv` stores config and I2C pointers, measured init values, and the cached tuned frequency.

## Control flow and integration
The `.c` file uses these constants in attach, init, and tuning. The frequency limits and step feed `dvb_tuner_ops.info`. The offset and step define PLL divider math in `qt1010_set_params()`. The operation type drives fixed init/tuning scripts and measurement helper dispatch.

## State and persistence
The private state fields `reg1f_init_val`, `reg20_init_val`, and `reg25_init_val` persist measurement-derived calibration values from init and are later reused in tuning register calculations. `frequency` stores the snapped RF frequency returned by `.get_frequency`.

## Dependencies
This header depends on `qt1010.h` for `struct qt1010_config` and on media/kernel unit macros such as `kHz` and `MHz` available through the included media headers.

## Risks and test signals
The register map is explicitly uncertain, with several comments marked unknown. Since this private header encodes frequency limits and offset math, mistakes propagate directly to tuning. Tests should validate that operation scripts do not exceed known register bounds, cached measurement fields are initialized before tuning, and frequency range/step metadata matches frontend expectations.
