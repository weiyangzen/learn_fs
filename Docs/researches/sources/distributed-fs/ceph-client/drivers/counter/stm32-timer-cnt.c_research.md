# sources/distributed-fs/ceph-client/drivers/counter/stm32-timer-cnt.c

Purpose: STM32 general-purpose timer counter/encoder driver with count, quadrature modes, capture events, overflow accounting, clock frequency reporting, and PM context restore.

Important APIs/types/functions: `struct stm32_timer_cnt` stores regmap, clock, ARR limit, enabled flag, suspend register backup, encoder capability, channel/IRQ counts, spinlock, and overflow count. Counter callbacks cover count read/write, function read/write, direction, ceiling, enable, prescaler, capture array, overflow count, action, events configuration, watch validation, and clock frequency signal extension. IRQ handler is `stm32_timer_cnt_isr()`.

Control flow: probe reads parent MFD data, detects encoder support by locating the timer-trigger child and checking its index, detects capture channels by probing CCER bits, requests global or update/capture IRQs when present, resets input selection, fills one count and five abstract signals, and registers. Function writes temporarily disable CEN, update slave-mode SMS, generate an update event, and restore CEN. Enable toggles TIM_CR1_CEN and the clock. Watch enable reconfigures DIER from the active counter event list and configures capture channels in input-capture mode; disabled captures are torn down. ISR filters SR by DIER, increments `nb_ovf`, pushes overflow/underflow and capture events, and clears handled flags.

State and persistence: hardware registers hold live count, mode, ARR, PSC, DIER/CCER/capture state. Driver caches enabled state, overflow count, detected topology, and suspend backup of CR1/CNT/SMCR/ARR. Overflow count is protected by spinlock. Enabled timers are restored after system sleep.

Dependencies and integration: depends on STM32 timers MFD definitions, regmap, clocks, pinctrl PM, OF child lookup, IRQs, and Generic Counter char-device events.

Risks: static signal layout intentionally exposes unused signals, so userspace must rely on action `none` rather than signal count for physical availability. Capture channel detection writes CCER temporarily and must not disturb active users. Event configuration writes all DIER bits from the watch list, so other timer consumers must not share the same hardware instance. Function writes restore full CR1 bits through `regmap_update_bits(..., TIM_CR1_CEN, cr1)`, relying on mask semantics.

Test signals: probe across timer instances with and without encoder support, channel detection counts, count write rejected above ARR, function mode transitions, prescaler and ceiling range checks, enable clock balancing, capture and overflow watch delivery through `/dev/counterN`, `num_overflows` synchronization, and suspend/resume preserving enabled registers.
