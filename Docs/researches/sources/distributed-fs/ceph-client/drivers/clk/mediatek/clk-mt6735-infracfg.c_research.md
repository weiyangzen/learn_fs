<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c

### Purpose
This driver registers MT6735 infrastructure gates and a mapped reset controller for infracfg resets.

### Important APIs, Types, And Functions
It defines infra reset/gate offsets, `infracfg_gates[]`, reset bank `infracfg_rst_bank_ofs[]`, logical-to-bank `infracfg_rst_idx_map[]`, `infracfg_resets`, `infracfg_clks`, and a simple platform driver for `mediatek,mt6735-infracfg`.

### Control Flow, State, And Persistence
The simple probe registers gate clocks and reset controller using the descriptor. Gate state persists in infra PDN registers; reset state persists in the INFRA reset bank with logical reset IDs translated by `rst_idx_map`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT clock/reset bindings, reset consumers, and common gate/reset helpers. Risks include incorrect reset ID mapping, critical APXGPT gating, and shared infra clocks being disabled by consumers. Test signals include infracfg provider registration, reset-controller users, timer stability, and peripheral probe coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c -->
