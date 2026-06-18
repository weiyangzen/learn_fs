# sources/distributed-fs/ceph-client/drivers/clocksource/timer-qcom.c

Purpose: Qualcomm KPSS/SCSS timer driver using GPT0 for per-CPU or shared one-shot clockevents and CPU0 DGT as clocksource/sched_clock/delay.

Important APIs/types/functions: global `event_base`, `sts_base`, and `source_base`; per-CPU `msm_evt`; `msm_timer_set_next_event()` clears/programs match and waits for pending clear if status exists. `msm_timer_init()` allocates events, requests percpu IRQ when applicable, installs CPU hotplug, registers clocksource/sched_clock/delay.

Control flow: DT init maps event base, parses IRQ index 1, reads optional `cpu-offset`, maps CPU0 source base separately, reads `clock-frequency`, sets DGT div4, computes source/event bases and reduced frequency, then calls common init. CPU startup initializes each clockevent and either enables percpu IRQ or requests shared IRQ. ISR stops oneshot timer then dispatches.

State/persistence: global MMIO bases and IRQ metadata; per-CPU event allocation persists. Source timer is enabled even if event setup failed because common init proceeds through `err` label to clocksource registration.

Dependencies/integration: compatibles `qcom,kpss-timer` and `qcom,scss-timer`, DT `clock-frequency`/`cpu-offset`, CPU hotplug, percpu IRQ, ARM delay timer.

Risks: event setup errors still fall through to clocksource registration; shared IRQ request on every CPU startup may be inappropriate if not percpu; fixed GPT_HZ for events while source frequency is divided DT frequency; busy-wait on clear-pending status can hang on bad hardware. Tests include percpu and non-percpu DTs, CPU hotplug, match clear polling, and DGT clocksource frequency.
