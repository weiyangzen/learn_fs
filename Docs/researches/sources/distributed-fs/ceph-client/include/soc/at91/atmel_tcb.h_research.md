# sources/distributed-fs/ceph-client/include/soc/at91/atmel_tcb.h

Purpose: defines the Atmel Timer/Counter Block shared data structures and register/bit definitions for three-channel TC blocks used by clock, PWM, capture, and timer drivers.

Important APIs and types: `struct atmel_tcb_config` describes counter width, generic clock support, and quadrature decoder support. `struct atmel_tc` tracks the platform device, mapped registers, block id, per-channel IRQs/clocks, slow clock, allocation list node, and allocation flag. `atmel_tc_divisors[]` exposes SoC-specific timer-clock divisors. Macros cover block control/mode registers, external clock routing, channel register addressing, channel control/mode fields, waveform/capture mode settings, counter/RA/RB/RC registers, status bits, interrupt registers, and all IRQ flags.

Control flow: clients allocate a TC block, configure block-wide external clock routing and optional synchronization, configure each channel in capture or waveform mode, enable clocks/IRQs, program compare/capture registers, and read/ack status.

State and persistence: runtime state is MMIO register configuration, enabled clocks/IRQs, driver allocation ownership, and per-channel timer state. No persistent storage is involved.

Dependencies and integration points: depends on platform devices, clocks, lists, and `__iomem`. Integrates clocksource, PWM, input/capture, quadrature, and board-specific timer users.

Risks and test signals: risks include shared block allocation conflicts, IRQ sharing mistakes, wrong clock divisor assumptions, capture/waveform bit overlap misuse, and missed status clear semantics. Test all three channels, shared/per-channel IRQ variants, PWM waveform generation, capture edge modes, block synchronization, clock gating, and suspend/resume.
