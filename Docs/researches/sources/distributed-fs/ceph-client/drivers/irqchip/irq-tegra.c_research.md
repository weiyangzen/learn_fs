# sources/distributed-fs/ceph-client/drivers/irqchip/irq-tegra.c

## Purpose
Implements NVIDIA Tegra legacy interrupt controllers as hierarchical filters above the GIC. It manages up to six 32-line ICTLR blocks, local enable/EOI/retrigger registers, and wake state for suspend.

## Important APIs, Types, And Functions
`struct tegra_ictlr_info` stores per-controller MMIO bases and, under PM, saved CPU/COP enable/class registers plus wake masks. The irq chip wraps parent mask/unmask/eoi/retrigger/type/affinity and overrides wake handling. Domain callbacks translate GIC-style DT specifiers and allocate parent IRQs.

## Control Flow
OF init locates the parent GIC domain, matches the expected controller count, maps each ICTLR region, disables CPU interrupts, selects IRQ class, creates a hierarchy domain, and registers syscore PM when enabled. Allocation validates SPI specifiers, installs the Tegra chip with the relevant block base as chip data, then allocates the same parent GIC interrupt.

## State And Persistence
Global `lic` and `num_ictlrs` describe the singleton controller set. Suspend saves CPU/COP enable and class registers, disables all interrupts, and enables only wake masks. Resume restores saved class and enable state. Wake masks are driver state only and intentionally do not call into the parent GIC.

## Dependencies And Integration Points
Depends on OF address matching for `nvidia,tegra20-ictlr`, `tegra30`, and `tegra210`, GIC binding constants, hierarchy domains, and syscore PM.

## Risks
DT region count mismatches expected SoC data are only warnings, so wrong DT can still boot with missing interrupt lines. Wake support bypasses the GIC and relies on ICTLR wake capability. The singleton design assumes one controller node.

## Test Signals
Verify controller count on Tegra20/30/210, child interrupt delivery through GIC, mask/unmask/EOI/retrigger behavior, CPU affinity forwarding, and suspend/resume wake masks per ICTLR block.
