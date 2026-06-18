# sources/distributed-fs/ceph-client/include/linux/fsl/ftm.h

Purpose: defines register offsets and bit masks for the NXP/Freescale FlexTimer Module used by timer, PWM, capture/compare, and quadrature decoder drivers.

Important APIs and types: register offsets cover status/control, counter, modulo, initial count, status, mode, sync, output init/mask, combine, deadtime, external trigger, polarity, fault status/control, filters, quadrature decoder, configuration, software output, PWM load, and channel control/value registers. Bit masks define clock source/prescaler, overflow flags/interrupts, mode enable/write-protect, quadrature decoder bits, fault status, channel mode bits, and maximum prescaler.

Control flow: drivers compute offsets with `FTM_CSC(channel)` and `FTM_CV(channel)`, program mode/control registers, set clock/prescaler/modulo, enable interrupts or PWM/capture features, and handle errata such as unusable quadrature filter bits.

State and persistence: this is runtime hardware register state. No persistent kernel data is defined.

Dependencies and integration points: consumed by FTM clocksource, PWM, counter, or platform drivers that map the FTM MMIO block.

Risks and test signals: risks include register offset drift between SoCs, prescaler miscalculation, write-protect handling, and errata bits that read as tied zero. Tests should cover timer overflow interrupts, PWM generation, capture/compare, quadrature mode without filters, suspend/resume, and invalid channel bounds.
