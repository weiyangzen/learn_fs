# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/clps711x.h

## Purpose

This 90-line header defines CLPS711X system control and status register offsets and bit masks for legacy ARM SoC peripherals.

## Important APIs, Types, and Functions

It exports `SYSCON_OFFSET`, `SYSFLG_OFFSET`, SYSCON1/2/3 macros for keyboard scan, timers, buzzer, debug, LCD, codec, SIR, ADC clock, wake, UART/serial, DRAM, SSI, clock, DAI, and power bits, plus SYSFLG1/2 and generic UART busy/FIFO status bits.

## Control Flow

No local flow exists. CLPS711X platform drivers use syscon/regmap updates and reads to enable peripherals, select clocks, and inspect status.

## State and Persistence Behavior

System control bits persist in SoC registers and control peripheral clocks/functions. Status flags reflect live hardware state such as UART FIFOs, reset, power fail, card detect, and SSI bus state.

## Dependencies and Integration Points

It integrates CLPS711X syscon users across keyboard, timers, LCD, serial, audio/DAI, ADC, buzzer, and power/status drivers.

## Risks and Edge Cases

Several macros encode values by masking inputs; callers must pass already sensible values. Shared system registers require masked writes to avoid disabling unrelated peripherals.

## Test Signals

Build coverage for CLPS711X drivers, peripheral enable/disable tests, status bit read tests, and static checks for masked update usage.
