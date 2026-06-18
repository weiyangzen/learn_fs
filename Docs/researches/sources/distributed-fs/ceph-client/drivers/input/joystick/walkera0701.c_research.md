# sources/distributed-fs/ceph-client/drivers/input/joystick/walkera0701.c

Purpose: decodes a Walkera WK-0701 RC transmitter connected through a parallel port into joystick axes and one gear key.

Important APIs/types/functions: `struct walkera_dev` stores the 25-nibble frame buffer, IRQ timing, sampled ACK bit, input device, hrtimer, parport, and pardevice. Core functions are `walkera0701_irq_handler`, `timer_handler`, `walkera0701_parse_frame`, `walkera0701_open`, `walkera0701_close`, `walkera0701_attach`, and `walkera0701_detach`.

Control flow: attach binds only the configured `port` module parameter, requires a parport IRQ, registers an exclusive parport device with an IRQ callback, negotiates compatibility mode, initializes an hrtimer, allocates input, and registers axes. On open it claims the parport and enables IRQs. Each falling-edge IRQ measures pulse width since the last edge, cancels the sample timer, detects sync pulses, records binary high-bit and analog 3-bit values, and when 25 entries are available validates two CRC groups and reports decoded channels. The hrtimer samples ACK midway between binary pulse lengths.

State and persistence: this driver supports one global static device. Frame assembly, timing, ACK state, and sync counter persist in RAM while open. There is no persistent configuration apart from the module parameter.

Dependencies and integration: uses parport IRQ callbacks, hrtimer, ktime nanosecond timing, and Linux input. It reports `BUS_PARPORT` and ABS_X/Y/Z/THROTTLE/RUDDER/MISC plus `BTN_GEAR_DOWN`.

Risks: pulse-width constants and tolerances are hardware/timing sensitive. A global singleton prevents multiple devices. IRQ/timer races are handled by `hrtimer_try_to_cancel`, but resync is conservative. Parse code reports no `input_sync`, so consumers rely on subsequent events or may see batched state differently than expected.

Test signals: verify with real transmitter pulses, test sync recovery after malformed timings, validate CRC rejection, check IRQ enable/disable on open/close, observe reported axes and gear key through `evtest`, and confirm detach ignores nonmatching ports.
