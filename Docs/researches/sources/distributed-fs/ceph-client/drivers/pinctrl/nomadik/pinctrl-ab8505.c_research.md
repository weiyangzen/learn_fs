# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8505.c

Purpose: this file provides AB8505-specific pin, group, function, alternate-function, and interrupt-cluster data to the common ABx500 pinctrl/GPIO driver.

Important APIs, types, and functions: `ab8505_pins[]` lists sparse GPIO-capable pins up to GPIO53. `ab8505_pinranges[]` maps sparse ranges to the altsetting needed for GPIO. `ab8505_groups[]` covers default, ALT_A, ALT_B, and ALT_C groups for sysclkreq, GPIO, PWM, ADI2, external control, modem I2C, reset/service, high-quality clock, PDM, UART data, external vibrator PWM, and USB VDAT. `ab8505_functions[]` maps function names to those groups. `ab8505_alternate_functions[]` encodes GPIOSEL and ALTFUN bits. `ab8505_gpio_irq_cluster[]` maps interrupt-capable GPIO clusters. `abx500_pinctrl_ab8505_init()` returns `ab8505_soc`.

Control flow: when the common core probes `stericsson,ab8505-gpio`, it calls this file's init function and then uses the returned table for pinctrl registration, GPIO range registration, pinmux changes, pin configuration, and GPIO-to-IRQ mapping.

State and persistence behavior: the file is table-only and keeps no runtime state. Mux and GPIO state persists in AB8505 hardware registers accessed by the common ABx500 core.

Dependencies and integration points: dependencies include the ABx500 header and AB8500/AB9540 interrupt constants from the MFD headers. It integrates with the AB8500 MFD IRQ domain through clusters for GPIO10-11, 13, 40-41, 50, and 52-53.

Risks and test signals: the GPIO number space is very sparse, so absent GPIOs must not be requested even though `ngpio` spans the highest range. `ab8505_functions[]` contains `FUNCTION(extvibra)` twice, which exposes duplicate function entries and may confuse function-count/debug users. Test sparse GPIO request failures, GPIO-to-IRQ mapping for AB9540 interrupt constants, ALT_B/ALT_C encoding on GPIO13 and GPIO50, and duplicate function behavior in pinctrl debugfs.
