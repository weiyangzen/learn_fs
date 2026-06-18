# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.c

## Purpose
This file provides the board configuration and frontend initialization for the Hopper VP-3028 DVB-T card.

## Important APIs, Types, and Functions
It defines `hopper_vp3028_config` for the ZL10353 demodulator, `vp3028_frontend_init`, and exported `struct mantis_hwconfig vp3028_config` with model/type, TS size, UART parameters, frontend callback, power GPIO, and reset GPIO.

## Control Flow
Frontend init toggles reset low, powers the frontend, waits, deasserts reset, powers on again, waits for hardware stabilization, then calls `dvb_attach(zl10353_attach, ...)` on the Mantis I2C adapter. It returns failure if power-on or frontend attach fails.

## State and Persistence Behavior
The file stores static board configuration only. Runtime state changes are hardware GPIO/power/reset lines and the DVB frontend object attached by the core.

## Dependencies and Integration Points
It depends on the ZL10353 frontend driver, Mantis GPIO/power helpers, Mantis DVB attach flow, and the Hopper PCI table that references `vp3028_config`.

## Risks
The local `fe` parameter is assigned but not stored by this function, so correctness depends on the broader Mantis attach convention. Timing delays and reset/power GPIO definitions are board-specific. Returning `-1` instead of a conventional errno on attach failure can affect diagnostics.

## Test Signals
Probe VP-3028 hardware, validate frontend I2C detection at address 0x0f, tune DVB-T channels, suspend/resume or reset cycles, and inject power/attach failures.
