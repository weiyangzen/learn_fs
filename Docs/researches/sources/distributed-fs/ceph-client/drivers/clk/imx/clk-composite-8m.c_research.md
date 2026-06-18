## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-8m.c

### Purpose
`clk-composite-8m.c` implements i.MX8M composite root clocks made of mux, predivider/postdivider, and gate components with SoC-specific quirks.

### Important APIs, Types, And Functions
Important ops are `imx8m_clk_composite_divider_*`, `imx8m_clk_composite_mux_*`, and `imx8m_clk_composite_gate_*`. The exported constructor `__imx8m_clk_hw_composite()` creates the composite and selects behavior based on `IMX_COMPOSITE_CORE`, `IMX_COMPOSITE_BUS`, and `IMX_COMPOSITE_FW_MANAGED`.

### Control Flow
Rate recalculation applies predivider and postdivider. Set-rate brute-force searches divider pairs for closest output, updates both fields under lock, and writes if changed. Mux set-parent may write the register twice for core/bus interfaces. The constructor allocates mux, divider, and gate components, chooses ops/flags, and uses a no-disable gate op when `mcore_booted` is true.

### State, Persistence, And Dependencies
State persists in CCM root registers. Allocated component structs hold register pointers and flags. Dependencies include CCF composite registration, global `imx_ccm_lock`, and global `mcore_booted`.

### Integration Points
i.MX8M SoC drivers use this for CPU, bus, and peripheral clock roots. Firmware-managed roots avoid parent-gate flags, and M-core state protects shared clocks from disable.

### Risks
Divider search may choose a rate with nonzero error without reporting the error. Gate disable is intentionally a no-op when M-core is booted, which can surprise unused-clock cleanup. Mux double-write is hardware-specific and should not be generalized blindly.

### Test Signals
Validate rate rounding across divider combinations, parent switching, M-core boot behavior, firmware-managed roots, and debugfs rates against register fields.
