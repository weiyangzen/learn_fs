## sources/distributed-fs/ceph-client/drivers/mfd/wm8994-regmap.c

Purpose: this file supplies the device-specific regmap data for WM1811, WM8994, and WM8958 variants. It defines reset/default values, readable-register predicates, volatile-register predicates, and exported regmap configurations used by `wm8994-core.c` after the chip identity is known.

Important APIs, types, and functions: `wm1811_defaults[]`, `wm8994_defaults[]`, and `wm8958_defaults[]` are the cache seed tables. `wm1811_readable_register()`, `wm8994_readable_register()`, and `wm8958_readable_register()` define valid bus-visible registers by chip variant. `wm8994_volatile_register()`, `wm1811_volatile_register()`, and `wm8958_volatile_register()` prevent caching of reset, status, interrupt, DSP, firmware, and selected GPIO/status registers. Exported objects are `wm1811_regmap_config`, `wm8994_regmap_config`, `wm8958_regmap_config`, and minimal `wm8994_base_regmap_config`.

Control flow: there is no runtime control loop beyond regmap callbacks. The core driver starts with the base config for early ID access, then calls `regmap_reinit_cache()` with the full variant config. Read/write calls from codec, GPIO, regulator, IRQ, and core paths are filtered and cached through these callbacks. Variant readable predicates build on one another: WM8994 adds registers to WM1811, and WM8958 adds DSP/MBC/firmware registers to WM8994.

State and persistence: reset defaults cover power management, analog mixers, LDOs, MICBIAS, clocks, FLLs, AIFs, filters, DRC/EQ coefficients, routing, GPIOs, interrupt masks, and WM8958 DSP/MBC registers. Volatile lists keep live status from becoming stale in the regcache. WM1811 has a customer/revision-dependent volatile treatment for GPIO6, read from driver data.

Dependencies and integration points: depends on `linux/regmap.h`, `linux/mfd/wm8994/core.h`, and register macro definitions. The regmap configs are directly consumed by the WM8994 core and indirectly by all child MFD functions sharing the parent regmap.

Risks and test signals: stale or incomplete default tables can cause incorrect cache restore after reset or suspend. Missing readable entries can make valid hardware accesses fail; missing volatile entries can cache changing status. Test signals include regmap debugfs/default comparisons, successful cache sync after runtime resume, interrupt status reads not being served stale, and variant-specific register access for WM8958 DSP/MBC and WM1811 GPIO6 behavior.
