# sources/distributed-fs/ceph-client/drivers/input/misc/kxtj9.c

Purpose: I2C input driver for Kionix KXTJ9 accelerometers, reporting ABS_X/Y/Z using polling or data-ready IRQ mode.

Important APIs/types/functions: depends on `struct kxtj9_platform_data`, I2C/SMBus, input polling, threaded IRQs, sysfs attributes, and PM ops. `struct kxtj9_data` stores client, copied platform data, input device, poll interval, shift, and cached control registers. Main routines are I2C read/report, g-range and ODR update, enable/disable, poll, ISR, verify, probe, suspend, and resume.

Control flow: probe checks I2C capabilities and platform data, runs optional platform init, verifies WHO_AM_I `0x07/0x08`, allocates input, sets ABS ranges, sets polling if no IRQ, registers input, and requests threaded IRQ if present. Input open powers on, programs control/interrupt/g-range/ODR, enables outputs, and clears initial interrupt. Close powers off.

State/persistence: cached register values and `last_poll_interval` are runtime state. Sysfs `poll` is visible only in IRQ mode and updates ODR under input mutex with IRQ disabled. Suspend/resume only act when input is enabled.

Dependencies/integration: legacy I2C ID `kxtj9`, board platform data, optional IRQ, input ABS axes.

Risks: no platform data means no probe. Sysfs ODR update ignores errors. Axis mapping/negation are trusted. Power hook failures can leave partial state.

Test signals: polling and IRQ modes, WHO_AM_I rejection, power hooks, sysfs polling, ODR table, g-range shifts, axis mapping/negation, INT_REL clearing, open/close, and PM paths.
