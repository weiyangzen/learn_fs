<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h

## Purpose
`drxk_map.h` is the DRX-K register-address and bitfield map used by `drxk_hard.c`. It defines symbolic addresses, masks, bit positions, reset/preload values, and command constants for the audio, FEC, IQM, OFDM, QAM, SCU, SIO host interface, bootloader, power, pad, GPIO, and token-ring blocks.

## Important APIs, Types, and Functions
The file contains only preprocessor constants. Major register families include `AUD_COMM_EXEC__A`, `FEC_*`, `IQM_*`, `OFDM_*`, `QAM_*`, `SCU_RAM_*`, `SCU_COMM_EXEC__A`, `SIO_TOP_*`, `SIO_HI_RA_RAM_*`, `SIO_CC_*`, `SIO_OFDM_SH_*`, `SIO_BL_*`, and `SIO_PDR_*`. Field constants use suffixes such as `__A` for address, `__M` for mask, `__B` for bit shift, and `__PRE` for preset/default values.

Notable command and state constants include SCU demodulator commands (`SCU_RAM_COMMAND_CMD_DEMOD_RESET`, `SET_ENV`, `SET_PARAM`, `START`, `GET_LOCK`, `STOP`), standard selectors (`SCU_RAM_COMMAND_STANDARD_QAM`, `STANDARD_OFDM`), OFDM synchronization-controller commands and auto flags, QAM lock encodings, bootloader modes, host-interface bridge command parameters, power-domain levels, and MPEG pad inversion/drive masks.

## Control Flow
The map is a compile-time dependency for all DRX-K hardware control flow. `drxk_hard.c` uses these constants to format I2C reads/writes, send HI/SCU/OFDM commands, load firmware and ROM tap tables, configure QAM and OFDM blocks, control MPEG output, poll lock state, compute statistics, and manage power. The `scu_command()` implementation explicitly asserts that `SCU_RAM_PARAM_0__A - SCU_RAM_PARAM_15__A == 15`, so the relative layout of SCU parameter registers is part of the executable contract.

## State and Persistence
The header defines addresses for volatile device state rather than storing state itself. State touched through these symbols includes FEC measurement periods and counters, IQM rate offsets, OFDM lock parameters, QAM loop coefficients and signal powers, SCU command/result RAM, pad drive configuration, bootloader transfer descriptors, and power/reset control. There is no persistent storage in the file.

## Dependencies and Integration Points
`drxk_map.h` is included by `drxk_hard.h`, which is included by `drxk_hard.c`. Its constants encode the DRX-K hardware ABI; changing names, masks, or addresses directly impacts I2C register transactions and firmware command semantics.

## Risks and Edge Cases
The map has no include guard in the visible source and is intended for single private inclusion through `drxk_hard.h`. Incorrect address, mask, or bit constants can compile cleanly but break hardware sequencing. Several constants are paired across low/high register words or mask/shift definitions, so partial edits can corrupt frequency-offset, AGC, QAM, or MPEG configuration. Generated-style names are long and similar across OFDM/QAM/SCU families, making copy/paste mistakes likely.

## Test Signals
The strongest signals are hardware-level: successful device initialization, firmware/tap loading, DVB-C and DVB-T lock, correct MPEG TS output polarity/format, valid BER/SNR/statistics, working I2C bridge and power transitions, and absence of `SCU not ready`, `SIO not ready`, or I2C register errors. Build-time validation should also catch the SCU parameter register layout assertion in `scu_command()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_map.h -->
