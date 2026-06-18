# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-gpio.c

`wm8350-gpio.c` provides exported GPIO pin configuration support for WM8350. It programs direction, function mux, polarity/type, pull-up/pull-down state, interrupt inversion, and debounce.

Important helpers are `gpio_set_dir()`, `wm8350_gpio_set_debounce()`, `gpio_set_func()`, `gpio_set_pull_up()`, `gpio_set_pull_down()`, `gpio_set_polarity()`, `gpio_set_invert()`, and exported `wm8350_gpio_config()`. The public helper first enforces pull-up/pull-down mutual exclusion, then applies invert, polarity, debounce, direction, and mux function. Direction and function writes temporarily unlock protected registers through `wm8350_reg_unlock()` and relock afterward.

There is no local persistent state; configuration persists in PMIC GPIO registers. Dependencies are WM8350 core register/security helpers and GPIO/PMIC definitions. Integration consumers are board code and GPIO-related child drivers that need pin mux setup.

Risks: GPIO number is not validated before several bit shifts; unlock/lock return values are ignored in direction/function helpers; partial configuration is not rolled back on later failure; mux handling supports GPIO 0-12 only. Test signals include per-pin mux writes, pull transition checks, invalid GPIO handling, and verifying the security lock is restored.
