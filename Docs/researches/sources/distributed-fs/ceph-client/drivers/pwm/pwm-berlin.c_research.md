# sources/distributed-fs/ceph-client/drivers/pwm/pwm-berlin.c

Purpose: implements the four-channel Marvell Berlin PWM controller.

Important APIs/types/functions: `struct berlin_pwm_chip` stores clock, MMIO base, and per-channel suspend backups. `berlin_pwm_config()` converts period/duty into timer count and optional 4096 prescale. `berlin_pwm_set_polarity()`, `berlin_pwm_enable()`, `berlin_pwm_disable()`, and `berlin_pwm_apply()` implement the PWM operations. PM callbacks save and restore enable/control/duty/count registers.

Control flow: probe maps MMIO, enables the clock, registers four PWMs, and stores the chip for PM. Apply disables when changing polarity, programs duty/period, then enables if the channel was previously off. Suspend saves all channel registers and disables the clock; resume reenables and restores them.

State and persistence: suspend state is cached in `channel[]`. Runtime output configuration lives in hardware registers and PWM core requested state. There is no `get_state` callback.

Dependencies and integration: depends on common clock, MMIO, OF compatible `marvell,berlin-pwm`, and PM sleep callbacks.

Risks and test signals: comments document misleading hardware prescaler behavior; only no-prescale and 4096-prescale are useful. There is no explicit guard for zero period before dividing duty by period. Test signals include prescale boundary, polarity changes while active, suspend/resume restore, disabled channel behavior, and period zero validation through the core.
