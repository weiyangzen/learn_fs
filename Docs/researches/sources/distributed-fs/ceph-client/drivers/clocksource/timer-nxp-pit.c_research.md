# sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-pit.c

Purpose: NXP/Freescale Periodic Interrupt Timer driver supporting DT early init for VF610 and platform-driver probing for S32G2, with channel 2 as clocksource and channel 3 as per-CPU clockevent.

Important APIs/types/functions: `struct pit_timer` embeds clockevent and clocksource; per-CPU `pit_timers` maps CPU slots. Helpers enable/disable module/timer, set counters, and ack IRQ. `pit_timer_init()` handles one hardware instance; `pit_clockevent_starting_cpu()` registers CPU-local events via hotplug.

Control flow: init maps base, IRQ, clock, disables module, registers channel-2 source/sched_clock, initializes channel-3 event and IRQ for `pit_instances`, enables module, increments instance count, and when all expected instances are present installs a CPU hotplug state. Event programming disables channel, writes `delta - 1`, and enables interrupt. ISR acks, disables in oneshot because hardware auto-reloads, then dispatches.

State/persistence: global instance counters and `max_pit_instances` govern multi-instance setup. `sched_clock_base` points to the last clocksource channel. Per-CPU pointers persist allocated PIT objects.

Dependencies/integration: compatibles `fsl,vf610-pit` and `nxp,s32g2-pit`, platform driver match data, CCF clocks, CPU hotplug, IRQ affinity.

Risks: each PIT instance registers a clocksource, potentially multiple sources; error unwind after hotplug setup is incomplete; `sched_clock_base` may be overwritten by later instances; oneshot is software-emulated over repeating hardware. Tests should cover S32G2 two-instance CPU affinity, VF610 single instance, channel selection, and no repeated oneshot interrupts.
