<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h

## Purpose
`stb0899_reg.h` is the STB0899 register and bitfield map used by the main driver and acquisition algorithms. It names S1 demod/FEC registers, S2 demod/FEC indirect base/offset pairs, GPIO/I2C/clock registers, and bit masks with matching offset/width macros.

## Important APIs, Types, And Functions
There are no functions. The important API is macro naming consistency: each field used with `STB0899_GETFIELD()` or `STB0899_SETFIELD_VAL()` must provide `STB0899_OFFST_<field>` and `STB0899_WIDTH_<field>`. The map includes device ID, timing/carrier/data status (`DSTATUS`, `TLIR`, `RTF`, `VSTATUS`, `PLPARM`), symbol-rate and derotator registers (`SFR*`, `CFR*`), S1 FEC controls, DiSEqC registers, GPIO/clock/I2C repeater registers, S2 demod UWP/CSM/BTR/CRL/equalizer/acquisition registers, and S2 FEC/LDPC/BCH registers. `STB0899_S2DEMOD` and `STB0899_S2FEC` define the indirect I2C device selectors.

## Control Flow
The header drives almost every register access in `stb0899_drv.c` and `stb0899_algo.c`. Init tables in `stb0899_cfg.h` are built from its offset/base macros. Search algorithms read lock/status fields and write loop/acquisition fields through this map. Delivery switching uses clock-stop and FEC fields; I2C gate control uses `STB0899_I2CRPT`/`STB0899_I2CTON`.

## State And Persistence
The file is compile-time hardware metadata. It does not store runtime state, but incorrect definitions directly corrupt persistent demodulator register state during operation.

## Dependencies And Integration Points
It is included by STB0899 driver and algorithm files and indirectly supports board init tables. Its macro names must remain aligned with the private bitfield helpers in `stb0899_priv.h`.

## Risks And Test Signals
Risks include typoed field names, wrong widths/offsets, duplicate or conflicting addresses, and fields with suspicious zero widths that can make generic bitfield helpers behave unexpectedly if used. Because S2 registers are accessed through an indirect protocol, base/offset mistakes are hard to diagnose. Test signals are successful compile of all referenced macros, attach core-ID reads, init table writes to intended S2 demod/FEC regions, lock-bit interpretation matching hardware traces, and regression coverage for I2C repeater, DiSEqC, GPIO, and clock gating fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_reg.h -->
