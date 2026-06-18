## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pli1209bc.c

Purpose: supports the Vicor PLI1209BC digital supervisor, exposing page-1 BCM telemetry and optional VOUT regulator control while avoiding known capability-probing problems.

Important APIs, types, and functions: `pli1209bc_plat_data` disables capability probing. `pli1209bc_read_word_data()` rescales READ_POUT, and returns zero for READ_VOUT/temperature when status indicates power-good-not. `pli1209bc_info` defines two pages but only page 1 function bits, direct coefficients, write delay, and optional regulator descriptor `vout2`.

Control flow: probe assigns platform data and calls `pmbus_do_probe()`. PMBus core sees two pages but only builds hwmon attributes for page 1. Selected reads are intercepted for power scaling and off-state invalid-data suppression.

State and persistence behavior: no private allocation. The driver sets a 250 us write delay consumed by PMBus core access timing. Regulator state, if enabled, is handled by PMBus core operations.

Dependencies and integration points: depends on PMBus core, optional `CONFIG_SENSORS_PLI1209BC_REGULATOR`, and regulator framework. It imports `linux/pmbus.h` platform flags and PMBus namespace.

Risks and test signals: returning zero for off-state VOUT/temp hides invalid data but may be interpreted as a real zero. Test page-1-only attribute exposure, off/on BCM behavior, READ_POUT scaling, write delay effects, and regulator enable/voltage paths.
