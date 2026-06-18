# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-tpm.c

Purpose: i.MX7ULP TPM timer driver providing a free-running up-counting clocksource/sched_clock/delay timer and a channel-0 software-compare one-shot clockevent.

Important APIs/types/functions: global `counter_width` and `timer_base`; `to_tpm` static `timer_of`; helpers disable/enable the compare channel, acknowledge CH0F, and read `TPM_CNT`. `tpm_set_next_event()` writes `TPM_C0V` and checks for missed deadlines. `tpm_clockevent_init()` and `tpm_clocksource_init()` register framework devices.

Control flow: init enables the `ipg` clock first for register access, then `timer_of_init()` acquires base/clock/IRQ. It discovers counter width from `TPM_PARAM`, resets TPM state, clears W1C flags, sets prescaler to div8 for 32-bit or div128 for 16-bit, sets `MOD` to max for free-running mode, registers clockevent, then clocksource. IRQ acknowledges channel flag and invokes the event handler.

State/persistence: static base and counter width become read-mostly boot state. The TPM counter keeps running after initialization; clockevent state is controlled by channel mode/interrupt enable.

Dependencies/integration: compatible `fsl,imx7ulp-tpm`, named `ipg` and `per` clocks, `timer-of`, ARM delay timer and sched_clock when `CONFIG_ARM`, MMIO clocksource.

Risks: `timer_of_init()` failure after enabling `ipg` leaks that clock; busy-wait for C0V synchronization can spin if hardware misbehaves; 16-bit mode has lower rating/range; rate is shifted by prescaler and must match register setup. Test signals include 16-bit/32-bit DT coverage, no missed min-delta events under bus contention, and clocksource monotonicity.
