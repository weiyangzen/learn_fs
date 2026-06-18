# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_regs.h

## Purpose
`ni_labpc_regs.h` defines the Lab-PC register map and bit masks used by the common and ISA-DMA Lab-PC code. It centralizes 8-bit register offsets for status, command, FIFO, timer, DIO, calibration, EEPROM, and interval counter access.

## Important APIs, Types, And Functions
The header contains no functions. It defines status bits such as `STAT1_DAVAIL`, `STAT1_OVERRUN`, `STAT1_OVERFLOW`, `STAT1_GATA0`, `STAT2_OUTA1`, and `STAT2_FIFONHF`; command bit constructors and masks such as `CMD1_MA()`, `CMD1_GAIN()`, `CMD1_SCANEN`, `CMD2_SWTRIG`, `CMD2_HWTRIG`, `CMD3_DMAEN`, `CMD3_FIFOINTEN`, `CMD6_ADCUNI`, `CMD6_SCANUP`, and `CMD5_EEPROMCS`; and register offsets for ADC FIFO, DAC byte registers, 8255 DIO base, 8254 counters, caldac/EEPROM serial control, and interval counter programming.

## Control Flow
The macros are consumed by `ni_labpc_common.c` to build command-register shadows, program AI/AO/calibration/EEPROM paths, drain FIFOs, and decode interrupt status. `ni_labpc_isadma.c` uses terminal-count status and clear-register macros to integrate DMA completion with common interrupt handling.

## State And Persistence
The header defines symbolic access to hardware state but stores none. Its bit definitions directly shape the persistent command-register shadows in `struct labpc_private`.

## Dependencies And Integration Points
It depends only on `BIT()` being visible through included Linux headers in the consuming C files. It is included by common and ISA-DMA Lab-PC code and should remain bus-neutral because both I/O-port and MMIO front ends use the same offsets.

## Risks
Register aliases share offsets with read/write-specific meanings, such as `STAT1_REG`/`CMD1_REG` and `ADC_FIFO_REG`/`DMATC_CLEAR_REG`; using the wrong direction can corrupt hardware state. Comments mark `CMD4_REG` as "Command 3 reg", which appears to be a comment typo and should not drive code changes. Any offset or bit change affects all Lab-PC bus variants.

## Test Signals
Test signals are mostly compile/static and hardware-simulation checks: status bits decoded in interrupt paths, command shadows using the intended masks, DAC byte offsets for both channels, FIFO clear/read alias behavior, DMA terminal-count clear offset, Lab-PC-1200-only command 5/6 use, and no accidental dependency on bus type.
