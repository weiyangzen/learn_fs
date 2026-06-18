# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8864.c

Purpose: TI LP8864/LP8866 display LED driver with 16-bit little-endian regmap brightness control and detailed fault reporting.

Important APIs/types/functions: `struct lp8864_led` stores I2C client, LED class device, regmap, and a mask of already reported sticky LED faults. `lp8864_fault_check()` reports and clears supply, boost, and LED status faults. `lp8864_brightness_set()` maps LED class brightness to 16-bit hardware brightness. `lp8864_brightness_get()` maps hardware value back to LED class scale.

Control flow: probe requires a child LED node, enables optional `vled`, asserts optional enable GPIO high, initializes 16-bit regmap, selects register-controlled brightness in `USER_CONFIG1`, clears/reports existing faults, then registers one extended LED class device. Every brightness set checks faults before writing `BRT_CONTROL`.

State and persistence: brightness and fault-clear state are hardware registers. `led_status_mask` suppresses repeated warnings for sticky LED status bits until power-down. GPIO cleanup disables the chip through a managed action.

Dependencies and integration: depends on I2C, regmap with 16-bit little-endian values, regulator and GPIO frameworks, OF child node naming, and LED class.

Risks: `brightness_get()` returns an enum but returns negative errors cast as brightness on read failure. Fault-clearing writes rely on paired status/clear bit layout. Only one LED class device is registered even though hardware has multiple channels.

Test signals: fault injection for supply/boost/LED status, brightness set/get scale round trips, enable GPIO cleanup on probe failure/remove, regulator optional handling, and child-node validation.
