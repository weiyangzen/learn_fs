<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h

`stv0910_regs.h` is a generated-style register and bit-field map for the STV0910/STV0900-family demodulator. It has no executable code, but it is central to all register access in `stv0910.c`. Register macros use `RSTV0910_*` names with 16-bit addresses; field macros use `FSTV0910_*` packed values where high bits encode the register address and lower bits encode field offset and mask.

The header is organized by chip/global registers, P2 demodulator register bank, P1 demodulator register bank, stream merger/transport registers, DiSEqC registers, LDPC/BCH metrics, iteration controls, and test registers. P1 and P2 sections are mostly mirrored, which allows `stv0910.c` to select a base P2 macro plus `state->regoff` or use `SET_FIELD()` token-pasting against P1/P2 field names.

Important integration points include `RSTV0910_MID` for probe identity, `RSTV0910_Px_I2CRPT` for tuner repeater control, PLL registers (`NCOARSE*`, `SYNTCTRL`), demod acquisition registers (`DMDISTATE`, `DMDCFGMD`, `DSTATUS`, `DMDMODCOD`), timing/symbol-rate registers (`SFR*`, `TMGREG*`), C/N and power registers, Viterbi/FEC registers, packet delineator and stream-ID registers, TS output registers, BER counter registers, and DiSEqC FIFO/status/config registers.

State and persistence are hardware-facing: the header defines addresses only, while the implementation writes those addresses into device registers and maintains local shadow state separately. There is no persistent software storage.

Risks are definition drift and packed-field correctness. A single bad address, offset, or mask can corrupt unrelated demodulator state, especially because `write_field()` derives register, shift, and mask directly from these constants. Mirrored P1/P2 definitions must stay consistent for `state->regoff` and token-pasted macros to work. Test signals include compile-time use by `stv0910.c`, spot checks against datasheet values where available, runtime probe/tune success, and targeted tests of field writes for representative P1, P2, shared, TS, and DiSEqC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0910_regs.h -->
