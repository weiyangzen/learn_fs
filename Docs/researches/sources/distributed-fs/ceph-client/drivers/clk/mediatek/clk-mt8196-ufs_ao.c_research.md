# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ufs_ao.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ufs_ao.c

### Purpose
`clk-mt8196-ufs_ao.c` registers the MT8196 UFS always-on clock and reset controller. It gates UFSHCI UFS/AES, UniPro TX/RX/SYS/SAP, and PHY SAP clocks, and exposes UFS-related reset lines.

### Important APIs, Types, And Functions
Key objects are `ufsao0_cg_regs`, `ufsao1_cg_regs`, `GATE_UFSAO0`, `GATE_UFSAO1`, `ufsao_clks`, `ufsao_rst_ofs`, `ufsao_rst_idx_map`, `ufsao_rst_desc`, and `ufsao_mcd`. The reset descriptor uses `MTK_RST_SET_CLR` and `RST_NR_PER_BANK`.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the clock gates and reset controller for `mediatek,mt8196-ufscfg-ao`. Gate state is stored in UFS AO CG banks, and reset state is controlled through reset set/clear banks at 0x48 and 0x148. The driver has no custom runtime state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include UFS host/PHY consumers, parent clocks `ufs`, `aes_ufsfde`, and `clk26m`, and reset framework clients. Risks include reset bank indexing errors, storage boot failures if parent clocks are missing, and improper AES clock gating. Test signals include UFS host probe, reset-controller lookups, UFS link training, crypto path operation, and suspend/resume.
