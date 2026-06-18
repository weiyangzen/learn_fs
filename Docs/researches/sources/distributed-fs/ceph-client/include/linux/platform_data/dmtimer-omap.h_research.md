
# sources/distributed-fs/ceph-client/include/linux/platform_data/dmtimer-omap.h

## Purpose
This header defines TI OMAP dual-mode timer platform data and the timer operation table exported to timer consumers. It abstracts request, configuration, PWM/capture, counter, interrupt, and clock operations.

## Important APIs And Types
`struct omap_dm_timer_ops` contains function pointers for requesting timers by device tree node, id, or any free timer; freeing; enable/disable; IRQ and interrupt mask control; clock access; start/stop; clock source; load/match/PWM/capture/prescaler configuration; counter/capture/status reads; and counter/status writes. `struct dmtimer_platform_data` carries OMAP1 timer-source callback, capability and errata flags, context-loss callback, and pointer to the ops table.

## Control Flow, State, And Persistence
The header defines a callback-driven control path: consumers request a timer, program load/match/PWM/capture state, start it, handle interrupts, and release it. Runtime state lives in the timer driver and hardware; context-loss count lets consumers detect lost hardware state across low-power transitions.

## Dependencies And Integration Points
It integrates OMAP timer users with platform timer drivers, device tree nodes, clocks, IRQs, PWM/capture consumers, and PM context-loss tracking.

## Risks And Test Signals
Risks include mismatched ops table, missing context restore after PM, incorrect source clock selection, and interrupt mask/status misuse. Test signals include timer request/free cycles, IRQ delivery, PWM output, capture reads, suspend/resume with context-loss detection, and errata-specific paths.
