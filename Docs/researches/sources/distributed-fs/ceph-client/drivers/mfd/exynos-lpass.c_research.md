# sources/distributed-fs/ceph-client/drivers/mfd/exynos-lpass.c

## Purpose
`exynos-lpass.c` is the MFD parent for the Samsung Exynos5433 Low Power Audio Subsystem. It maps LPASS top registers, enables the control clock, unmasks selected interrupts, resets internal IP blocks, and populates child devices from device tree.

## Important APIs, Types, and Functions
`struct exynos_lpass` stores the top regmap and `sfr0_ctrl` clock. `exynos_lpass_core_sw_reset()` toggles reset bits. `exynos_lpass_enable()` enables the clock, unmasks SFR/DMA/I2S/UART interrupt paths, and resets I2S, DMA, memory, and UART. `exynos_lpass_disable()` masks interrupts and disables the clock. Probe, runtime PM callbacks, and the devm cleanup action manage lifecycle.

## Control Flow
Probe maps the TOP MMIO resource, gets the SFR clock, creates a 32-bit regmap, marks runtime PM active/enabled, calls `exynos_lpass_enable()`, registers a cleanup action that disables runtime PM and hardware, and finally populates child nodes. Runtime suspend disables the LPASS; runtime resume re-enables and resets it. System sleep uses forced runtime suspend/resume late hooks.

## State and Persistence
State is the regmap pointer and prepared clock. Hardware register state includes interrupt masks and reset lines. The driver does not save register contents; resume re-applies the enable/reset sequence.

## Dependencies and Integration Points
It depends on platform MMIO resources, clock framework, regmap-mmio, runtime PM, OF population, and Exynos PMU register definitions. Child audio IP blocks are instantiated from the device tree under the LPASS node.

## Risks and Edge Cases
`clk_prepare_enable()` return is ignored in `exynos_lpass_enable()`, so clock-enable failure could be hidden. Reset sequencing is fixed and may disturb child state if called while children are active. Interrupt mask semantics are hardware-specific; the code writes bit masks named as unmasked sources.

## Test Signals
Check clock enable/disable counts, TOP regmap access, interrupt mask values after probe/resume, reset toggles for each IP block, runtime suspend/resume with active child drivers, and OF child population.
