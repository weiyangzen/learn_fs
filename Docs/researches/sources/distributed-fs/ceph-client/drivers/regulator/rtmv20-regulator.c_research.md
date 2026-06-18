# sources/distributed-fs/ceph-client/drivers/regulator/rtmv20-regulator.c

Purpose: supports the Richtek RTMV20 laser switch/current regulator. It exposes one current regulator named `rtmv20,lsw`, configures many timing/current/polarity properties, handles hardware enable GPIO power-down, and reports laser-driver fault interrupts.

Important APIs/types/functions: `struct rtmv20_priv` stores device, regmap, enable GPIO, and regulator device. `rtmv20_lsw_set_current_limit()` maps current limits to selector values. `rtmv20_properties_init()` clamps and writes DT properties, including multi-byte big-endian fields. `rtmv20_irq_handler()` maps OTP/OCP/fail events to regulator notifiers.

Control flow: probe asserts required enable GPIO, waits for I2C readiness, initializes cached regmap, validates vendor ID, applies property defaults/overrides, then deliberately enters cache-only mode and disables hardware for low consumption. It registers the current regulator, unmasks events, and requests a threaded IRQ. Enabling reasserts GPIO, syncs cached registers, then sets regulator enable bits; disabling clears enable bits, cache-only marks dirty, and powers hardware off.

State and persistence: regcache preserves configuration while the chip is off. Hardware registers store timing, current, polarity, low-battery, FSIN/ES settings, masks, and event latches. No persistent state is written outside the chip.

Dependencies and integration: depends on I2C, required enable GPIO, regmap cache, regulator current APIs, IRQ, PM sleep hooks, and many Richtek DT properties.

Risks and test signals: probe disables hardware before writing `LDMASK`, then writes through a cache-only regmap; this should be checked against regmap semantics and intended unmask timing. IRQ request assumes a valid IRQ. Tests should cover property clamping and 16-bit writes, current limit rounding, enable/disable regcache sync, vendor mismatch, IRQ notifier mapping, and suspend/resume IRQ wake handling.
