# sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.c

Purpose: reset-controller bridge for MMP clock/reset bits, mapping reset specifier clock IDs to MMIO bit operations.

Important APIs/functions: `mmp_clk_reset_register` registers a `reset_controller_dev`. `mmp_of_reset_xlate` maps OF reset args to internal reset indexes. `mmp_clk_reset_assert` and `mmp_clk_reset_deassert` set or clear configured reset bits under optional locks.

Control flow: SoC files build `mmp_clk_reset_cell` arrays from APBC clock tables and call register. Consumers pass a clock ID in the reset specifier; xlate linearly searches cells for that ID, and reset ops operate on the matched register/mask.

State and persistence: `mmp_clk_reset_unit` and cell arrays persist after registration. Reset state is MMIO-backed.

Dependencies and integration: Linux reset-controller framework, OF phandles, MMP reset descriptors from `reset.h`, and shared APBC locks.

Risks: `flags` and `MMP_RESET_INVERT` are currently unused, so inverted reset support is declared but not implemented. Linear lookup is small but depends on unique clock IDs. No unregister path is provided.

Test signals: reset phandle resolution by binding IDs, assert/deassert register traces, device probe recovery after reset, and static checks for duplicate `clk_id` values.
