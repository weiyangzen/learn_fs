# sources/distributed-fs/ceph-client/drivers/regulator/rt6190-regulator.c

Purpose: supports the Richtek RT6190 high-voltage output regulator with large voltage/current ranges, active discharge, mode selection, runtime PM, optional hardware enable GPIO, ADC-related initialization, and IRQ-based error notification.

Important APIs/types/functions: `struct rt6190_data` stores regmap, optional enable GPIO, runtime PM device, and cached alert events. Raw little-endian helpers implement 16-bit voltage/current selector reads and writes. `rt6190_out_enable()` preserves output configuration across enable because the IC restores defaults. `rt6190_irq_handler()` caches write-cleared alert bits and emits regulator notifications.

Control flow: probe asserts optional enable GPIO, initializes a cached regmap, validates Richtek VID, writes initialization registers for ADC, ratio, masks, OCP, and bus-current ADC, enables runtime PM, registers the regulator, and requests IRQ if present. Enable gets runtime PM, snapshots VOUT/current registers, enables PWM, restores snapshot, and enables charge pump. Disable turns off charge pump/output, clears cached alert state, and releases runtime PM. Runtime suspend/resume powers hardware by GPIO and syncs regcache.

State and persistence: cached alert events keep fault history after IRQ write-clear until output disable. Regmap cache preserves configuration during GPIO-powered runtime suspend. Hardware stores selectors, current limit, mode, discharge, ADC, and status.

Dependencies and integration: depends on I2C, optional GPIO, runtime PM, regmap cache, regulator current-limit APIs, optional IRQ, and OF regulator init data.

Risks and test signals: enable error paths after `pm_runtime_get_sync()` do not visibly unwind with `pm_runtime_put()`. Voltage/current selectors use little-endian raw transfers, so bus ordering is important. Tests should cover enable restore semantics, current limit rounding, runtime suspend/resume, IRQ caching and notifier calls, VID mismatch, and optional IRQ/GPIO absence.
