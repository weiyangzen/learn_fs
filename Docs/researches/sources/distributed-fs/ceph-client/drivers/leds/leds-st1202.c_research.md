# sources/distributed-fs/ceph-client/drivers/leds/leds-st1202.c

Purpose: I2C LED class driver for the STMicroelectronics LED1202 12-channel constant-current LED controller, including brightness and hardware pattern sequence support.

Important APIs, types, and functions: `struct st1202_chip` stores the I2C client, mutex, and fixed channel array. `struct st1202_led` maps an active DT channel to a LED class device. `st1202_read_reg()`/`st1202_write_reg()` wrap SMBus byte access. `st1202_pwm_pattern_write()` and `st1202_duration_pattern_write()` program pattern RAM. `st1202_led_pattern_set()` writes up to eight pattern entries and starts the sequence. `st1202_setup()` resets/enables the device and clears channel enables.

Control flow: probe checks SMBus byte support, allocates state, initializes the chip, parses child nodes by `reg`, then for each active channel enables the channel, clears patterns, and registers a LED. Brightness has two paths: `brightness_set` writes the current register, while `brightness_set_blocking` toggles the channel enable bit.

State and persistence: channel active/fwnode data is stored in RAM; PWM/current values, channel enables, and pattern RAM are in chip registers. Device setup resets chip state on probe and remove relies on devm cleanup without explicit shutdown.

Dependencies and integration points: I2C SMBus byte data, OF child nodes, LED class pattern API, cleanup guards, and compatible `st,led1202`.

Risks and test signals: probe lacks an explicit bounds check before indexing `chip->leds[reg]`; DT validation should cover `reg < 12`. Test pattern duration min/max, eight-pattern limit, channel high/low enable register paths, concurrent brightness/pattern access under the mutex, and setup timing after reset.
