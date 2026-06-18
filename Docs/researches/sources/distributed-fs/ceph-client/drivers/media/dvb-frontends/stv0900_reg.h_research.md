# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_reg.h

## Purpose

`stv0900_reg.h` is the register and bit-field map for the ST STV0900 satellite demodulator driver. It does not implement demodulation logic itself; instead, it supplies the symbolic register addresses and encoded field descriptors consumed by `stv0900_read_reg()`, `stv0900_write_reg()`, `stv0900_get_bits()`, and `stv0900_write_bits()` users in the rest of the frontend driver. The file is foundational for both demodulator instances of the dual-demod STV0900 chip: many public-looking aliases are written against path-1 (`P1_`) addresses and shifted at runtime to path-2 (`P2_`) addresses by the `shiftx()` helper implemented in `stv0900_sw.c`.

## Important APIs, Macros, and Types

The file declares `extern s32 shiftx(s32 x, int demod, s32 shift);`, which is the only function-like dependency it introduces. `REGx(x)` and `FLDx(x)` wrap that helper with fixed shifts of `0x200` and `0x2000000`, respectively. The demodulator selection is implicit: the macros expect a local variable named `demod` to be in scope. That convention is heavily used by code such as `stv0900_sw.c`, where functions receive `enum fe_stv0900_demod_num demod` and then access aliases like `CFR2`, `AGC2I1`, `HEADER_MODE`, `DVBS1_ENABLE`, or `PKTDELIN_LOCK`.

Register macros follow two conventions. Raw macros such as `R0900_P1_DMDISTATE` and `R0900_P2_DMDISTATE` carry exact register addresses. Field macros such as `F0900_P1_HEADER_MODE` encode a register address plus bit mask/position information in the driver's packed format. Alias macros without the `P1_`/`P2_` prefix, for example `DMDISTATE`, `HEADER_MODE`, `CFRINIT1`, `AGC2REF`, `SYMB_FREQ3`, `CAR_FREQ2`, `VIT_CURPUN`, and `TSFIFO_LINEOK`, are the primary integration API for demodulator-specific driver logic.

## Register Coverage

The early global area covers chip identity, DACs, interrupt status/masks, I2C repeater controls, GPIO/pin multiplexing, standby/clock routing, stream status selectors, FSK transmit/receive configuration, DiSEqC transmit/receive controls, PLL/synthesis state, tuner test controls, and clock gating. These definitions are shared chip-level controls rather than per-demodulator algorithm state.

The per-demodulator register regions are extensive. The P2 block starts around `R0900_P2_IQCONST` and includes constellation symbol observation, AGC1/AGC2, demodulator mode and status, carrier/timing loops, symbol-rate loop registers, equalizer taps, noise estimates, carrier loop tuning for DVB-S2 modulations, PL scrambling roots, MODCOD enable masks, CCI/gaussian controls, demod result memory, FFE/equalizer controls, embedded tuner controls, Viterbi/FEC controls, packet delineator status and reset bits, transport-stream FIFO configuration/status, error counters, and FEC spy/BER meter registers. The P1 block mirrors this coverage starting at `R0900_P1_IQCONST`, and most driver-facing aliases are anchored to P1 definitions plus `REGx()`/`FLDx()` shifts.

## Control Flow and State Behavior

This header contributes to control flow indirectly. The packed field constants determine which hardware bit is read or written when the software state machine calls `stv0900_get_bits()` or `stv0900_write_bits()`. For example, the acquisition path in `stv0900_sw.c` reads `HEADER_MODE` to decide whether DVB-S, DSS, or DVB-S2 was found; writes `DVBS1_ENABLE` and `DVBS2_ENABLE` to constrain search standards; writes `SCAN_ENABLE` and `CFR_AUTOSCAN` for blind search; reads `TMGLOCK_QUALITY`, `AGC2I1`, `AGC2I0`, and `TSFIFO_LINEOK` for lock validation; and toggles `RST_HWARE`, `ALGOSWRST`, and `RESET_UPKO_COUNT` for hardware/software reset steps.

There is no persistent software storage in this header. Persistence is hardware-state persistence: any register write made through these definitions changes demodulator, tuner, FEC, DiSEqC, or transport-stream behavior until overwritten, reset, or power-cycled. Because aliases depend on the in-scope `demod`, a wrong demodulator number or missing `demod` local variable can redirect writes to the wrong register bank at compile time or runtime.

## Dependencies and Integration Points

`stv0900_reg.h` depends on Linux-style integer aliases such as `s32` being available before inclusion through the surrounding driver headers. It is included by implementation files such as `stv0900_sw.c` after `stv0900.h`, and works with the private register helpers declared/implemented in `stv0900_priv.h` and related driver files. The encoded register/field constants are coupled to helper routines that understand the STV0900 field encoding; they are not generic Linux regmap descriptors.

The most important integration point is the demodulator-bank abstraction. Driver logic usually writes aliases like `CFRINIT1` rather than selecting `R0900_P1_CFRINIT1` or `R0900_P2_CFRINIT1` manually. This keeps acquisition code mostly common across demodulators, but makes the macro contract unusually sensitive to naming and the exact `shiftx()` behavior.

## Risks

The largest risk is silent hardware misconfiguration. These constants encode register addresses and masks as magic numbers; a typo can affect unrelated hardware state and may only reproduce with a specific chip cut, demodulator path, modulation, or tuner configuration. The `REGx`/`FLDx` aliases also require a local `demod` symbol, which is easy to overlook during refactors and makes the header less self-contained than ordinary constants.

The file mixes exact P2 addresses, P1 addresses, and shifted aliases. Reviewers should be cautious around off-by-one or sign mistakes in `shiftx()` calls, especially where aliases use negative shifts or nonstandard shift values for DiSEqC/I2C repeater fields. Because the C implementation branches on `chip_id`, some fields are only meaningful for selected STV0900 revisions, but the header itself does not encode those applicability constraints.

## Test Signals

Useful validation signals are compile-time coverage of all alias macros used by the driver, probe/readback tests that confirm P1 and P2 aliases target the intended register banks, and hardware or emulator tests that exercise both demodulators. Functional tests should cover DVB-S1, DSS, DVB-S2, blind search, warm/cold search, DiSEqC transmit/receive, transport-stream lock, and BER/error-counter paths, because those are the main consumers of the field map. A focused regression test for `shiftx()` expectations is valuable: for demodulator 0 aliases should remain at P1 addresses, and for demodulator 1 they should shift to the corresponding P2 register/field encodings.
