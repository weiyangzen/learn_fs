# sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.c

Purpose: shared implementation for TI LP55xx programmable LED controllers. It provides register helpers, engine state transitions, firmware/program memory loading, LED and multicolor class registration, sysfs engine controls, DT parsing, clock/GPIO enable handling, and common probe/remove.

Important APIs/types/functions: exports `lp55xx_probe()`, `lp55xx_remove()`, `lp55xx_write/read/update_bits()`, `lp55xx_load_engine()`, `lp55xx_run_engine_common()`, `lp55xx_update_program_memory()`, `lp55xx_firmware_loaded_cb()`, brightness/current helpers, engine sysfs helpers, and master-fader helpers. Internally, `lp55xx_init_device()`, `lp55xx_register_leds()`, `lp55xx_register_sysfs()`, and `lp55xx_of_populate_pdata()` are the main orchestration points.

Control flow: chip-specific I2C drivers pass a `struct lp55xx_device_config` through match data. Probe obtains platform data or parses DT, validates program size, allocates LED slots, initializes enable GPIO/reset/detection/post-init, registers active LED channels, applies initial currents, and creates common and chip-specific sysfs groups. Engine sysfs selects an engine, optionally requests firmware asynchronously, loads ASCII-hex bytecode into program memory, then switches LOAD engines to RUN through OP_MODE/EXEC registers.

State and persistence: state is volatile and held in `struct lp55xx_chip` (`engine_idx`, `engines[]`, firmware pointer, mutex, LED count) and `struct lp55xx_led` (`chan_nr`, current, max current, brightness, multicolor metadata). Hardware registers persist only until chip reset/power loss. Firmware bytes are released after load, not retained.

Dependencies and integration: depends on I2C SMBus, LED class, LED multicolor class, firmware loader, GPIO descriptors, optional 32 kHz clock, OF parsing, and `dt-bindings/leds/leds-lp55xx.h`. Chip drivers integrate by filling `lp55xx_device_config` register addresses, callbacks, max channels, and optional attribute groups.

Risks: sysfs paths expose mutable engine/program state, so locking correctness is critical; most operations use `chip->lock`, but asynchronous firmware load depends on `engine_idx` remaining meaningful. Program parsing accepts ASCII hex and requires even byte count; malformed input returns `-EINVAL`. Shared PWM/fader register assumptions must match each chip config. `lp55xx_unregister_sysfs()` removes the common engine group unconditionally even when it may not have been created, relying on sysfs tolerance.

Test signals: unit or hardware tests should cover DT parsing for single and RGB LEDs, current bounds, firmware load size/format failures, engine mode transitions, mux parsing, master fader read/write, enable GPIO timing, external-clock selection, and remove-time shutdown.
