# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek.c

Purpose: MediaTek timer driver supporting two hardware models: older GPT blocks with clocksource plus clockevent, and newer system timer blocks providing one-shot clockevents only.

Important APIs/types/functions: one static `timer_of to` is configured differently by `mtk_gpt_init()` and `mtk_syst_init()`. GPT helpers stop/setup/start timers, configure free-running source timer 2, enable/ack IRQs, and manage suspend/resume. SYST helpers program countdown value and control register bits.

Control flow: GPT init sets clockevent callbacks and IRQ handler, calls `timer_of_init()`, configures timer 2 as free-running clocksource/sched_clock, configures timer 1 for events, registers clockevent, and enables its IRQ. SYST init assigns one-shot callbacks/handler, initializes resources, and registers clockevent. Event programming always disables/stops before writing compare/countdown and re-enables interrupt. Interrupt handlers acknowledge then invoke the event handler.

State/persistence: global `to` and `gpt_sched_reg` persist. GPT suspend disables and acknowledges all interrupts to avoid firmware suspend blockage; resume reenables the event IRQ.

Dependencies/integration: compatibles `mediatek,mt6577-timer` and `mediatek,mt6765-timer`, `timer-of`, clocksource/clockevents/sched_clock, DT IRQ and clock.

Risks: single static `to` prevents simultaneous GPT/SYST instances; GPT and SYST share names/global state; `mtk_gpt_suspend()` acknowledges all six timer IRQ bits; SYST lacks clocksource. Tests should cover both compatibles, IRQ ack behavior, suspend/resume, and clocksource selection on GPT platforms.
