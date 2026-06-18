# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp.h

Purpose: shared register definitions and small state structs for ARM SP804-style dual timers and Integrator variants.

Important APIs/types/functions: defines two timer base offsets, common register offsets, control bits for oneshot, 32-bit mode, divisors, interrupt enable, periodic, and enable. `struct sp804_timer` describes variant register layout and width, including HiSilicon 64-bit high-register offsets. `struct sp804_clkevt` stores resolved MMIO pointers and reload/width for a timer channel.

Control flow: none beyond data layout. `timer-sp804.c` and `timer-integrator-ap.c` consume the constants to program timer channels.

State/persistence: header-defined structs become caller-owned state. `NR_TIMERS` encodes the two-channel SP804 block assumption.

Dependencies/integration: used by SP804 and Integrator AP timer drivers; no standalone kernel registration.

Risks: constants annotate platform support in comments but no compile-time enforcement exists; mismatched variant width or offset tables can corrupt timer programming. Test signals are build coverage and runtime timer bring-up for ARM SP804, HiSilicon SP804, and Integrator platforms.
