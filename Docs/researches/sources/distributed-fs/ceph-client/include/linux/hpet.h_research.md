# sources/distributed-fs/ceph-client/include/linux/hpet.h

## Purpose
`hpet.h` defines kernel HPET register layout and allocation metadata. It mirrors the memory-mapped HPET block, timer register fields, capability/configuration masks, and the data structure used when registering an HPET instance.

## Important APIs, Types, And Functions
`struct hpet` models the HPET MMIO register block with capability, configuration, interrupt status, main counter, and flexible timer array. Nested `struct hpet_timer` models timer config/compare/FSB registers. `struct hpet_data` stores physical/MMIO address, IRQ count, allocation bitmask, and IRQ numbers. `hpet_reserve_timer()` marks a timer allocated, and `hpet_alloc()` registers/allocates an HPET described by `hpet_data`.

## Control Flow And State
Platform code fills `hpet_data`, reserves timers as needed, and calls `hpet_alloc()`. HPET implementation code maps registers, reads capabilities, configures counters/timers, routes interrupts, and records allocated timers in `hd_state`. Hardware state persists in MMIO registers; software state persists in `hpet_data`.

## Dependencies And Integration Points
It includes `uapi/linux/hpet.h` and uses `void __iomem`. It integrates with platform/ACPI discovery, clocksource/clockevent setup, interrupt routing, and the legacy HPET userspace API.

## Risks
Risks include incorrect MMIO structure assumptions, 32-bit versus 64-bit counter access, timer count/IRQ bounds, FSB routing bit mistakes, and allocation bit overflow if timer indices exceed supported width. Register fields are hardware ABI and must not be renumbered.

## Test Signals
Test HPET discovery/allocation, reserved timer masks, clockevent operation, periodic/one-shot timers, 32-bit counter mode, FSB interrupt routing, interrupt status clearing, and systems with maximum timer counts.
