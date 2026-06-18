# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max77620.c

## Purpose
Implements pinmux and pin configuration for MAX77620/MAX20024 PMIC GPIO pins. It selects alternate functions, configures pull-up/pull-down and drive mode, and stores flexible power sequencer settings for active and suspend states.

## Important APIs, Types, and Functions
Important types include `struct max77620_pctrl_info`, `struct max77620_pin_function`, `struct max77620_pingroup`, `struct max77620_pin_info`, and `struct max77620_fps_config`. Custom pinconf parameters map `maxim,active-fps-*` and `maxim,suspend-fps-*` properties. Runtime functions include `max77620_pinctrl_enable`, `max77620_pinconf_get`, `max77620_pinconf_set`, `max77620_get_default_fps`, `max77620_set_fps_param`, `max77620_pinctrl_suspend`, and `max77620_pinctrl_resume`.

## Control Flow and State
Probe inherits the parent firmware node, obtains the PMIC regmap from parent driver data, initializes FPS config caches to `-1`, fills static function/group metadata, and registers pinctrl. Mux setting writes one bit in `MAX77620_REG_AME_GPIO`, allowing GPIO mode or the one alternate function valid for the selected pin. Pinconf updates per-pin GPIO config registers for open-drain/push-pull, updates pull-up and pull-down registers as a mutually exclusive pair, and writes FPS source/power slot fields for GPIO1-GPIO3. Suspend/resume replay cached FPS settings from `fps_config[]`, switching between suspend and active values.

## Dependencies and Integration Points
Depends on the MAX77620 MFD parent, `linux/mfd/max77620.h` register definitions, regmap, platform device IDs `max77620-pinctrl` and `max20024-pinctrl`, generic pinconf DT parsing with custom properties, and PM sleep callbacks.

## Risks and Test Signals
Risks include cached drive type not reflecting hardware defaults until set, FPS cache values being skipped when left at `-1`, invalid FPS settings for pins outside GPIO1-GPIO3, alternate-function selector mismatches, and separate pull-up/pull-down writes leaving transient states on regmap errors. Test signals include muxing each GPIO to its legal alternate function, get-after-set for drive and pull configs, suspend/resume register readback for FPS fields, invalid-pin FPS tests, and PMIC GPIO consumers using both MAX77620 and MAX20024 IDs.
