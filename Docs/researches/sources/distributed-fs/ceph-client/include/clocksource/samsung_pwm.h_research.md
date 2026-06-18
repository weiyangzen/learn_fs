# sources/distributed-fs/ceph-client/include/clocksource/samsung_pwm.h

Purpose: shared Samsung PWM timer clocksource definitions.

Important APIs/types/functions: `SAMSUNG_PWM_NUM`, optional exported `samsung_pwm_lock`, `struct samsung_pwm_variant`, and `samsung_pwm_clocksource_init`.

Control flow: platform code passes PWM MMIO base, IRQ array, and variant capabilities to initialize clocksource use of PWM channels. The lock is shared only when the clocksource driver is compiled in.

State and persistence: variant metadata records bit width, divider base, masks, and tint status support. Runtime state is in implementation; lock coordinates shared PWM access.

Dependencies and integration points: depends on spinlock definitions and integrates with Samsung PWM driver and platform timer setup.

Risks: lock visibility differs by config, so users must match `CONFIG_CLKSRC_SAMSUNG_PWM`. Incorrect variant masks can corrupt PWM channels used by other subsystems.

Test signals: Samsung SoC boot tests, PWM driver coexistence tests, and timer interrupt validation.
