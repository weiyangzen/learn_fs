# sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9052_tsi.c

Purpose: `da9052_tsi.c` is a platform touchscreen driver for the Dialog DA9052 PMIC TSI block. It samples X/Y/Z pressure through DA9052 ADC registers and coordinates separate pen-down and TSI-ready IRQs.

Important APIs, types, and functions: `struct da9052_tsi` stores the DA9052 MFD pointer, input device, delayed pen work, stopped flag, and ADC-on flag. `da9052_ts_adc_toggle()` enables/disables continuous TSI conversion and mirrors `adc_on`. `da9052_ts_pendwn_irq()` masks pen-down, unmasks TSI-ready, enables ADC, and schedules polling work. `da9052_ts_datardy_irq()` reads and reports samples through `da9052_ts_read()`. `da9052_ts_pen_work()` polls pen status and on release disables ADC, reports release, clears events, and swaps IRQ masks. Probe configures GPIO mux, TSI timing/mode, LDO9 reference, IRQs, and input.

Control flow: probe allocates state and input manually, disables pen detect and ADC, requests DA9052 PENDOWN and TSIREADY IRQs, masks both, configures TSI hardware, registers input, and stores platform data. Input open clears `stopped`, enables PENDOWN, and enables the pen detect circuit. On pen-down IRQ the driver switches to data-ready sampling and schedules a 20 ms pen polling loop. Close stops polling, balances IRQ enable counts if ADC was active, disables ADC and pen detect.

State and persistence: runtime state is `stopped`, `adc_on`, delayed work, and DA9052 register/IRQ mask state. Removal restores LDO9 to `0x19`, frees IRQs, unregisters input, and frees memory. No persistent calibration exists.

Dependencies and integration points: it relies on DA9052 MFD register and IRQ APIs, platform device `da9052-tsi`, Linux input, delayed work, and PMIC register definitions.

Risks: probe uses non-devm allocation and manual unwind, so error paths must stay balanced. `da9052_ts_adc_toggle()` ignores register update errors but updates `adc_on` regardless. The pen polling work treats read errors as pen still down, which may keep polling indefinitely until close. The FIXME acknowledges unhandled IRQ issues on quick pen down/up sequences.

Test signals: validate GPIO/TSI register programming, pen-down IRQ mask transition, data-ready sample reporting, release polling and pressure-zero report, close with ADC active, IRQ balancing, removal restore of LDO9, and quick tap behavior.
