# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-sysctr.c

Purpose: NXP i.MX system counter compare driver used as a one-shot clockevent against a 64-bit free-running system counter.

Important APIs/types/functions: `struct sysctr_private` stores CMPCR baseline and low/high counter offsets. `to_sysctr` is a static `timer_of` requesting base, clock, and IRQ. `sysctr_read_counter()` performs stable high/low/high reads. `sysctr_set_next_event()` programs `CMPCV_HI/LO`, `sysctr_timer_enable()` toggles compare enable, and `sysctr_timer_interrupt()` disables/acknowledges before dispatching.

Control flow: `__sysctr_timer_init()` allocates private data, calls `timer_of_init()`, optionally divides the clock rate by `SYS_CTR_CLK_DIV` unless `nxp,no-divider` is present, stores CMPCR with EN cleared, and sets CPU mask/private data. The standard and i.MX95 init wrappers choose different read offsets and register the clockevent. Events disable compare, read current 64-bit counter, add delta, write compare high/low, and re-enable.

State/persistence: static `to_sysctr` and heap private data persist for boot lifetime. CMPCR base bits are preserved so enable/disable does not clobber other compare control bits.

Dependencies/integration: `timer-of` helper, DT compatibles `nxp,sysctr-timer` and `nxp,imx95-sysctr-timer`, named clock `per`, one IRQ, clockevents core.

Risks: no clocksource registration here, so another system counter source must exist; singleton `to_sysctr`; allocation is not freed on later success; low/high offset selection must match SoC; compare high is masked to 20 bits. Tests should verify correct DT property clock divider, one-shot delivery, no stale ISTAT after shutdown, and i.MX95 offset coverage.
