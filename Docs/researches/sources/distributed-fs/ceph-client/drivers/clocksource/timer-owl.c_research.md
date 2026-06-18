# sources/distributed-fs/ceph-client/drivers/clocksource/timer-owl.c

Purpose: Actions Semi Owl timer driver using one internal timer slice as clocksource/sched_clock and another as one-shot clockevent.

Important APIs/types/functions: global base pointers select overall, source, and event timer blocks. `owl_timer_reset()` clears CTL/VAL/CMP; `owl_timer_set_enabled()` toggles enable while clearing PD semantics. `owl_timer_set_next_event()` programs compare and interrupt. `owl_timer_init()` maps resources and registers frameworks.

Control flow: init maps base, derives source base at `+0x08` and event base at `+0x14`, gets named IRQ `timer1`, gets the clock rate, resets/enables source, registers sched_clock and MMIO clocksource, resets event, requests IRQ, sets cpumask/IRQ, and registers one-shot dynamic IRQ clockevent. ISR writes PD to acknowledge pending event then dispatches.

State/persistence: global MMIO pointers persist. Source timer runs continuously; event timer is reset or enabled per callback.

Dependencies/integration: compatibles `actions,s500-timer`, `actions,s700-timer`, `actions,s900-timer`, named IRQ, CCF clock, OF mapping.

Risks: derived offsets must match SoC layout; clock is not explicitly prepared/enabled before `clk_get_rate()`; init error paths do not unmap; oneshot resume callback is a no-op. Test signals include named IRQ resolution, clocksource count, event compare interrupts, and PD acknowledgement behavior.
