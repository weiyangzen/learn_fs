# sources/distributed-fs/ceph-client/kernel/irq/settings.h

## Purpose
`settings.h` centralizes internal accessors for `irq_desc->status_use_accessors`, replacing direct use of IRQ status macros and making descriptor settings changes explicit.

## Important APIs, types, and functions
It defines internal `_IRQ_*` aliases for settings bits, intentionally poisons direct macro names such as `IRQ_PER_CPU` and `IRQ_LEVEL`, and provides inline helpers including `irq_settings_clr_and_set()`, `irq_settings_is_per_cpu()`, `irq_settings_is_per_cpu_devid()`, `irq_settings_set_per_cpu()`, `irq_settings_set_no_balancing()`, `irq_settings_get_trigger_mask()`, `irq_settings_set_trigger_mask()`, `irq_settings_is_level()`, request/thread/probe/autoenable checks and setters, nested-thread and polled checks, disable-unlazy helpers, hidden checks, and no-debug helpers.

## Control flow
There is no runtime control flow beyond inline bit tests and mutations. Callers in genirq code use these helpers while holding the appropriate descriptor locks or during initialization.

## State and persistence
The header mutates only `desc->status_use_accessors`. The state is descriptor-local and runtime-only, though it strongly affects whether IRQs can be requested, probed, threaded, balanced, displayed, autoenabled, debugged, or treated as level/per-CPU.

## Dependencies and integration points
It depends on IRQ flag definitions from public genirq headers and is included by internal IRQ subsystem files such as management, PM, procfs, resend, and spurious handling. The macro poisoning enforces use of accessors inside the IRQ core.

## Risks and test signals
Risks include callers bypassing accessors, modifying flags without required locking, confusing irqdata flags with descriptor settings, and trigger-level settings getting out of sync with irqchip programming. Test signals include builds catching poisoned macro use, requestability/threadability/probeability transitions, trigger changes through `__irq_set_trigger()`, per-CPU and hidden IRQ behavior, and no-debug/spurious detector interactions.
