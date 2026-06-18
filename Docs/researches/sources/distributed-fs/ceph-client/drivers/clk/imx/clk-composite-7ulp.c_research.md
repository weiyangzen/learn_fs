## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-7ulp.c

### Purpose
`clk-composite-7ulp.c` creates composite peripheral clock gates for i.MX7ULP and i.MX8ULP PCC registers, optionally combining mux, fractional divider, gate, and software-reset release.

### Important APIs, Types, And Functions
`pcc_gate_ops` wraps standard gate behavior and releases `SW_RST` after enable. `imx_ulp_clk_hw_composite()` is the shared constructor. Public wrappers are `imx7ulp_clk_hw_composite()` and exported `imx8ulp_clk_hw_composite()`.

### Control Flow
The constructor first checks the PCC present bit and returns NULL for absent clocks. It allocates requested mux/divider/gate components, optionally assigns `imx_ccm_lock`, gates clocks during initialization to allow parent/rate programming, and registers a composite clock with gate/rate/parent constraints. Enable with `has_swrst` turns on the gate, waits briefly, sets reset-release bit, reads back, and delays again.

### State, Persistence, And Dependencies
Clock configuration persists in PCC registers. Driver state consists of allocated component objects owned by CCF. It depends on fractional-divider helpers and i.MX global locking.

### Integration Points
Used by ULP SoC clock tables for peripheral clock control. It is exported for i.MX8ULP module users.

### Risks
Returning NULL for not-present clocks requires callers to tolerate absent entries. Initial gating can change bootloader-enabled hardware state. Allocation failure unwinds only locally before registration. Software reset semantics apply only to clocks passed with `has_swrst`.

### Test Signals
Test present and absent PCC entries, parent/rate changes only while gated, peripheral reset release after enable, and i.MX8ULP module symbol resolution.
