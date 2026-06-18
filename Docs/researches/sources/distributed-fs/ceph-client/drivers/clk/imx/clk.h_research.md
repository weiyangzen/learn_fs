# sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h

### Purpose
`clk.h` is the shared private interface for i.MX clock drivers. It defines common PLL metadata, helper prototypes, and macro wrappers that turn common clock framework registrations into compact i.MX-specific declarations with consistent locking and flags.

### Important APIs, Types, And Functions
The header declares PLL families (`imx_pllv1_type`, `imx_pllv3_type`, `imx_pllv4_type`, `imx_pll14xx_type`, `imx_fracn_gppll_clk`, `imx_pll14xx_clk`), PFD/composite helpers, gate/mux/divider constructors, `to_clk()`, fixed-clock helpers, and SoC-specific composite APIs for i.MX7ULP, i.MX8ULP, i.MX8M, and i.MX93. It also declares globals such as `imx_ccm_lock` and `mcore_booted`.

### Control Flow, State, And Persistence
Most wrappers are inline or macro-level policy: gates, muxes, and dividers are registered with `imx_ccm_lock`; many clocks default to `CLK_SET_RATE_PARENT` or `CLK_SET_RATE_NO_REPARENT`; gate2 helpers encode i.MX CGR fields; composite helpers layer i.MX8M bus/core/firmware-managed flags. The header itself has no persistent state, but it standardizes how stateful register-backed clocks in C files use common spinlock protection and clock flags.

### Dependencies, Integration Points, Risks, And Test Signals
This header depends on Linux common clock provider APIs, bit helpers, and the implementation files for each declared PLL/composite type. It is a high-impact integration point because many SoC clock tables rely on its flag defaults. Risks include macro argument side effects, flag policy changes affecting broad clock trees, incorrect parent-rate propagation, and prototype drift with implementation files. Test signals are all i.MX clock driver build coverage, lockdep around shared CCM registers, rate propagation tests, and boot checks for SoCs using each PLL/composite helper family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk.h -->
