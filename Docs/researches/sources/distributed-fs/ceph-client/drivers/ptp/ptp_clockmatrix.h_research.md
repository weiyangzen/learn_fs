# sources/distributed-fs/ceph-client/drivers/ptp/ptp_clockmatrix.h Research

## Purpose
`ptp_clockmatrix.h` defines the private constants and state structures for the ClockMatrix PHC driver.

## Important APIs, Types, And Functions
The header defines firmware filename `idtcm.bin`, hardware limits (`MAX_TOD`, `MAX_PLL`, `MAX_REF_CLK`), write-phase limits, mask register addresses, default ToD-to-PLL/output mappings, firmware version enum, PTP PLL operating mode enum, and the `IDTCM_FW_REG()` compatibility macro. `struct idtcm_channel` captures one ToD/PTP channel's clock info, PTP clock, register bases, PLL mapping, mode transition callbacks, phase-pull-in state, current frequency, DCO delay, trigger reference, and output mask. `struct idtcm` captures device-wide state, regmap, lock, version, masks, delayed EXTTS work, event routing, and overhead timing. `struct idtcm_fwrc` describes packed firmware records.

## Control Flow
The header has no executable flow, but its callback fields drive runtime mode transitions: each channel stores functions for configuring write-frequency/write-phase mode and selecting firmware or software phase pull-in.

## State And Persistence
The structures declared here are the driver's durable in-memory state for each probed device and channel. Their values mirror persistent hardware state programmed into ClockMatrix registers.

## Dependencies And Integration Points
It depends on PTP clock types, regmap, `ktime`, and ClockMatrix register definitions from `linux/mfd/idt8a340_reg.h`. It is consumed only by `ptp_clockmatrix.c`.

## Risks
Constants in this header encode hardware register contracts. Wrong defaults can expose the wrong ToD as a PHC, align PPS to incorrect outputs, or use the wrong firmware-era register. The packed firmware record layout must match the firmware binary exactly.

## Test Signals
Tests should validate default masks, firmware-record parsing size/alignment, version-dependent register macro expansion, channel array bounds, and max phase/frequency limits used by PTP caps.
