# sources/distributed-fs/ceph-client/include/linux/mfd/ingenic-tcu.h

Purpose: This header maps the Ingenic JZ47xx Timer/Counter Unit registers shared by watchdog, clocksource/clockevent, and PWM users.

Important APIs, types, and constants: Register macros define watchdog timer data/control/count/CSR registers, global timer enable/status/flag/mask/stop registers, per-channel data-full/data-half/count/CSR registers, OST registers, and test registers. Field macros define parent clock selection, prescaler bits, PWM shutdown/initial-level/output-enable bits, watchdog enable, channel stride, and per-channel register address helpers `TCU_REG_TDFRc`, `TCU_REG_TDHRc`, `TCU_REG_TCNTc`, and `TCU_REG_TCSRc`.

Control flow, state, and persistence: There are no functions. Consumers enable/disable channels through global set/clear registers, program channel counters and compare values, and use CSR bits to select clock source/prescaler or PWM output behavior. State is hardware timer counts, flags, masks, enable bits, and watchdog state.

Dependencies and integration points: The header depends on bitops and integrates with Ingenic clocksource, clockevent, watchdog, PWM, and possibly regmap/syscon style access.

Risks and test signals: Risks include channel-stride mistakes, reserved CSR bits being overwritten, wrong parent clock selection, and watchdog enable sequencing. Test signals include timer interrupt accuracy, PWM duty/period tests, watchdog reset tests, channel enable/disable idempotence, and suspend/resume timer retention behavior.
