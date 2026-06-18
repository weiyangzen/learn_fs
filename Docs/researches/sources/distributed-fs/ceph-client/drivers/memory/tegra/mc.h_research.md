# sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.h

Purpose: private Tegra memory-controller header containing common register offsets, error bit definitions, inline MMIO helpers, SoC externs, shared reset ops, IRQ handler declarations, and internal ICC node IDs.

Important APIs/types/functions: defines MC interrupt/status bits, EMEM arbitration/timing registers, error-status field masks, channel and MSS/Tegra264 register offsets, `MC_BROADCAST_CHANNEL`, `tegra_mc_scale_percents()`, `icc_provider_to_tegra_mc()`, `mc_ch_readl()`, `mc_ch_writel()`, `mc_readl()`, `mc_writel()`, SoC extern declarations, `tegra30_mc_probe()`, `tegra30_mc_handle_irq()`, and `TEGRA_ICC_MC/EMC/EMEM` IDs.

Control flow: included by `mc.c` and SoC table files. Inline accessors route broadcast and per-channel MMIO through the appropriate register bases and gracefully return/do nothing if channel broadcast registers are absent.

State and persistence: no independent state. It defines how driver state in `struct tegra_mc` is interpreted when accessing registers and ICC providers.

Dependencies and integration: includes Linux bits/I/O/types and public `<soc/tegra/mc.h>`. It bridges the common driver, SoC description files, SMMU, reset, interrupt, and interconnect code.

Risks: shared register constants are consumed across many SoCs; adding newer SoC fields can accidentally affect older decode paths. `mc_ch_readl()` returning zero when no broadcast channel exists can hide accidental channel access in code that should use `mc_readl()`. Internal ICC IDs must not collide with DT node IDs.

Test signals: compile all Tegra MC variants, validate 32-bit and 64-bit address error decoding, test channel and non-channel SoCs, and run interconnect provider setup using the reserved internal ICC IDs.
