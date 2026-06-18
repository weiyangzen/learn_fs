# sources/distributed-fs/ceph-client/drivers/input/joystick/n64joy.c

Purpose: Platform driver for Nintendo 64 console controller ports, supporting up to four non-hotpluggable controllers through the N64 SI/PIF hardware.

Important APIs/types/functions: `struct n64joy_priv` stores aligned SI buffer, timer, mutex, input devices, MMIO register base, and open count. `struct joydata` overlays PIF response data with controller fields. `n64joy_exec_pif()` performs SI DMA write/read to PIF RAM with cache maintenance and IRQ-off critical section. `n64joy_poll()` reports buttons and signed X/Y axes. `n64joy_probe()` scans controllers at init and registers inputs.

Control flow: Module init uses `platform_driver_probe()`; probe maps SI registers, executes scan PIF commands, registers an input device for each connected controller ID, and returns `-ENODEV` if none found. Opening the first input starts a 16 ms timer; polling executes PIF commands and reports all registered controller states; closing the last input deletes the timer.

State and persistence: Controller presence is scanned once at init and stored in `n64joy_dev[]`. Open count controls timer lifetime. No module unloading support is provided; comments explain init memory is freed for an embedded RAM-constrained target.

Dependencies and integration points: Platform MMIO resource, N64 SI registers/PIF RAM physical address, cache maintenance functions, input core, timers, and mutex guards.

Risks: Busy-waiting SI status can hang if hardware stops responding. No hotplug support. `n64joy_opened` is `u8`, so many opens could overflow in theory, though input open counts are normally bounded by users. Direct hardware/cache operations are architecture-specific.

Test signals: N64 hardware or emulator with 0..4 controllers; scan ID validation; open/close timer count; SI DMA busy handling; axes signedness and button mapping; no-controller probe return.
