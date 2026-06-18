# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.h

## Purpose
`fsl_spdif.h` defines the Freescale/NXP S/PDIF register map, control/status bit fields, interrupt masks, clock divider fields, gain and TX-rate enums, IEC958 buffer sizes, and supported ALSA rate/format masks used by `fsl_spdif.c`.

## Important APIs, Types, And Functions
There are no functions. The important definitions are register offsets such as `REG_SPDIF_SCR`, `REG_SPDIF_SRPC`, `REG_SPDIF_SIE/SIS/SIC`, data/status registers, extended 192-bit channel-status registers, SCR FIFO/DMA/TXSEL fields, SRPC DPLL/clock/gain fields, interrupt masks, STC clock divider fields, `enum spdif_gainsel`, `enum spdif_txrate`, `SPDIF_CSTATUS_BYTE`, `SPDIF_UBITS_SIZE`, `SPDIF_QSUB_SIZE`, and playback/capture rate and format masks.

## Control Flow
The header shapes runtime flow by defining which SCR bits are toggled at startup/shutdown/trigger, which interrupts are enabled and cleared in the ISR, how SRPC clock source and gain are encoded for RX DPLL measurement, and how STC encodes TX clock source, TX divider, system divider, and all-clock enable.

## State And Persistence
No storage is allocated here. The defined register fields are cached through regmap in the C file, while data sizes determine persistent channel-status and subcode buffers in `struct spdif_mixer_control`.

## Dependencies And Integration Points
The file assumes ALSA PCM rate and format constants are available through the including C file. It provides the low-level hardware constants for ASoC DAI callbacks, IEC958 kcontrols, regmap access tables, and runtime PM restore logic in `fsl_spdif.c`.

## Risks And Edge Cases
The interrupt and register constants are reused as read and write-clear addresses (`REG_SPDIF_SIS` and `REG_SPDIF_SIC` share an offset), so regmap writeability and clear semantics must match hardware. The extended channel-status registers are only valid for selected SoCs. Playback and capture support different formats and rates, and capture is fixed to 24-bit unless raw capture mode is enabled by the C file.

## Test Signals
Compile-time users should catch missing constants. Runtime evidence includes correct IRQ clearing, valid STC divider programming for each `enum spdif_txrate`, correct RX DPLL rate calculation using `SRPC` and `SRFM`, and working 192-bit channel-status writes on SoCs that set `cchannel_192b`.
