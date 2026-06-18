# sources/distributed-fs/ceph-client/include/linux/pwm_backlight.h

Purpose: defines platform data for the generic PWM backlight driver.

Important APIs and types: `struct platform_pwm_backlight_data` carries max/default/low-threshold brightness, PWM period, optional brightness levels table, on/off delays, and callbacks for init, brightness notify, post-notify, and exit.

Control flow: board/platform code supplies this data to the PWM backlight driver; the driver initializes hardware, maps brightness through levels or linear range, applies PWM duty, calls notify hooks around changes, and delays around power transitions.

State and persistence: platform data is static configuration. Runtime brightness and PWM state are managed by the backlight driver and PWM framework.

Dependencies and integration points: depends on backlight subsystem and PWM consumer API. Integrates board-specific panel/backlight sequencing with the generic driver.

Risks and test signals: risks include invalid brightness defaults, level table lifetime, wrong PWM period units, callback failures, and delay ordering causing panel artifacts. Test brightness changes, suspend/resume, init/exit hooks, notify transformations, and level-table mapping.
