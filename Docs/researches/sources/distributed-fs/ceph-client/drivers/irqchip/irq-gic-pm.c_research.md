# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-pm.c

## Purpose
Wraps a child ARM GIC instance with runtime PM and clock management, used for NVIDIA Tegra AGIC-style controllers.

## Important APIs, Types, and Functions
`struct gic_clk_data` describes required clocks. `struct gic_chip_pm` stores GIC data, clock metadata, and bulk clock handles. Runtime PM callbacks are `gic_runtime_resume()` and `gic_runtime_suspend()`. `gic_probe()` initializes clocks, PM, and the child GIC via `gic_of_init_child()`.

## Control Flow
Probe matches clock data, maps a parent IRQ, allocates clock descriptors, enables runtime PM, resumes to turn clocks on, initializes the child GIC, then releases the runtime PM reference. Runtime suspend saves distributor/CPU interface state and disables clocks. Runtime resume enables clocks and restores saved GIC state after the first initialization pass.

## State and Persistence
Device-managed `gic_chip_pm` persists as driver data. `chip_data` is intentionally NULL during first resume to avoid restoring before initialization. GIC save/restore state is held by core GIC data. Clock enable state follows runtime PM.

## Dependencies and Integration Points
Depends on platform driver probing, OF match data, clock bulk APIs, runtime PM, parent IRQ parsing, and ARM GIC child initialization/save/restore helpers.

## Risks and Test Signals
Risks include clock enable failures, parent IRQ mapping leaks, restore-before-init ordering, and runtime PM imbalance. Test signals include AGIC registration log, clocks toggling around runtime suspend/resume, interrupts surviving PM cycles, and no `irq_dispose_mapping` leak on probe failure.
