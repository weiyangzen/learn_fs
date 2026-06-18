# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt312_priv.h

## Purpose
`mt312_priv.h` defines the private register-address enum and model-id enum for the MT312 family driver.

## Important APIs, Types, And Functions
`enum mt312_reg_addr` maps demodulator registers from status, FEC, LNB, SNR, AGC, reset, DiSEqC, symbol-rate, Viterbi, sweep, monitor, test, and config areas. It also includes ZL10313-only aliases `HW_CTRL` and `MPEG_CTRL`. `enum mt312_model_id` names `ID_VP310`, `ID_MT312`, and `ID_ZL10313`.

## Control Flow
No executable flow. The C file uses these enum values for all I2C register access and model-specific branching.

## State And Persistence
The header defines register constants and model ids only. Hardware register values are transient demodulator state.

## Dependencies And Integration Points
It is private to `mt312.c` and intentionally not part of the board-driver API.

## Risks
Some enum values overlap for model-specific registers (`HW_CTRL` with `VIT_ERRPER_M`, `MPEG_CTRL` with `VIT_ERRPER_L`), so callers must use them only for the proper chip. Numeric changes break hardware programming.

## Test Signals
Attach/init/status/tune tests on VP310, MT312, and ZL10313 validate the register map indirectly; compile-only coverage is insufficient.
