# sources/distributed-fs/ceph-client/drivers/bus/ts-nbus.c

## Purpose
`ts-nbus.c` implements the Technologic Systems NBUS used by TS-4600 boards to communicate with FPGA peripherals over GPIO lines and a PWM-driven FPGA clock.

## Important APIs, Types, And Functions
`struct ts_nbus` owns the PWM, eight data GPIO descriptors, control GPIOs (`csn`, `txrx`, `strobe`, `ale`, `rdy`), and a mutex. Exported APIs `ts_nbus_read()` and `ts_nbus_write()` provide 16-bit register access for child drivers. Probe gathers GPIOs with devm GPIO APIs, configures the PWM, stores the bus instance as drvdata, and populates child platform devices.

## Control Flow
Read and write operations take the mutex for atomic bus access. Reads set TX/RX to read mode, write the address with ALE asserted, switch data GPIOs to input, then read two bytes MSB-first while checking `rdy`. Writes set TX/RX to write mode, write the address, write two value bytes MSB-first, then pulse `csn` until `rdy` reports completion. Probe initializes GPIOs, enables the PWM at full duty cycle, and calls `of_platform_populate()` so child devices can use the exported bus helpers.

## State And Persistence
State is mostly physical line state plus the PWM enable state. The driver persists no register cache; each operation bit-bangs the bus. Removal disables the PWM under the same mutex to stop the FPGA-facing clock.

## Dependencies And Integration Points
The driver depends on devicetree GPIO names `ts,data`, `ts,csn`, `ts,txrx`, `ts,strobe`, `ts,ale`, `ts,rdy`, a PWM provider, and `linux/ts-nbus.h` consumers. Child devices use the parent drvdata and exported GPL symbols to access FPGA registers.

## Risks And Edge Cases
The read path loops while `rdy` is nonzero and the write path spins until `rdy` clears without timeout, so broken hardware or GPIO wiring can hang callers. GPIO array ordering must match bit order. Direction changes around reads must be restored to output even on errors. PWM period validation catches an unusable PWM state, but runtime PWM failures after probe are not retried.

## Test Signals
Probe should log initialization and populate expected children. Hardware tests should cover repeated reads/writes, wrong-address behavior, concurrent child access, PWM disable on remove, GPIO error injection, and a wedged `rdy` line to expose lack of timeout.
