# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.h

Purpose: defines GR2D register offsets that contain memory base addresses and the register count used for firewall bitmap sizing.

Important APIs/types: macros cover regular and SB variants of source, destination, pattern, and U/V base address registers. `GR2D_NUM_REGS` defines the upper bound for `DECLARE_BITMAP(addr_regs, GR2D_NUM_REGS)`.

Control flow and state: no runtime logic; the constants seed `gr2d_addr_regs[]` in `gr2d.c`.

Dependencies/integration: consumed by `gr2d.c` and indirectly by command-stream firewall validation.

Risks: missing a new address register would weaken submit validation; an incorrect `GR2D_NUM_REGS` could cause valid offsets to be ignored.

Test signals: firewall tests for each defined address register and compile-time coverage through `gr2d.c`.
