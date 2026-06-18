# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.h

Purpose: shared contract between SharpSL board files and the common SharpSL power driver.

Important APIs/types/functions: defines `struct sharpsl_charger_machinfo` callback/data table, `struct battery_thresh`, `struct battery_stat`, `struct sharpsl_pm_status`, charger mode constants, PM flag bits, LED values, MAX1111 channel constants, global `sharpsl_pm`, threshold arrays, and prototypes for `sharpsl_battery_kick()`, `sharpsl_pm_led()`, and `sharpsl_pm_pxa_read_max1111()`.

Control flow: no executable flow; consumers fill `sharpsl_charger_machinfo`, pass it as platform data to the `sharpsl-pm` device, then the driver calls these hooks for charger, ADC, suspend, wake, and backlight decisions.

State and persistence: describes in-memory driver state, timers, flags, charger mode, charge start time, and last sampled battery fields. Persistent effects are indirect through hardware callbacks.

Dependencies and integration points: integrated by `sharpsl_pm.c` and model-specific files such as `spitz_pm.c`. The data IDs map the common driver to board-specific ADC/GPIO reads.

Risks: callback polarity and threshold mistakes can produce unsafe charger behavior. The global state export couples board code tightly to one device instance.

Test signals: compile coverage catches signature drift; runtime validation needs board callback tests for every `SHARPSL_*` data selector and threshold table.
