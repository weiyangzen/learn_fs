# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8860.c

Purpose: TI LP8860 display-cluster/backlight LED driver using regmap, optional regulator, optional enable GPIO, fault clearing, and optional EEPROM programming.

Important APIs/types/functions: `struct lp8860_led` holds mutex, I2C client, LED class device, and regmap. `lp8860_fault_check()` reads LED and general fault registers and clears them. `lp8860_brightness_set()` scales LED class brightness into 16-bit display brightness registers. `lp8860_program_eeprom()` unlocks, writes a static EEPROM table, locks, and triggers programming when module parameter `program_eeprom` is set.

Control flow: probe requires one child LED node, enables optional `vled`, drives optional enable GPIO, creates an 8-bit regmap with an access table, optionally programs EEPROM, then registers one extended LED class device with default label `:display_cluster`. Brightness writes clear faults first, then write MSB/LSB.

State and persistence: normal brightness is volatile register state. EEPROM programming is persistent on the chip and intentionally guarded by a module parameter because endurance is limited. Faults are read and cleared opportunistically on brightness/programming operations.

Dependencies and integration: depends on I2C, regmap, regulator framework, GPIO descriptors, OF LED init data, module parameters, and LED class.

Risks: EEPROM table is hard-coded; enabling `program_eeprom` on production systems can consume EEPROM cycles or install wrong panel settings. Brightness scale uses `brt_val * 255`, producing 0..65025 instead of full 0xffff. Fault check clears faults without surfacing which fault occurred.

Test signals: probe with/without GPIO and regulator, brightness writes at 0/255, fault-clear behavior, regmap access limits, EEPROM path only in controlled hardware tests, and missing child-node failure.
