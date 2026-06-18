## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-exclusive.c

### Purpose
`clk-gate-exclusive.c` implements an i.MX gate that refuses to enable when mutually exclusive bits in the same register are already active.

### Important APIs, Types, And Functions
`struct clk_gate_exclusive` embeds `clk_gate` and an `exclusive_mask`. `clk_gate_exclusive_enable()` checks the mask before delegating to standard gate ops. `imx_clk_hw_gate_exclusive()` registers the clock.

### Control Flow
Enable reads the gate register and returns `-EBUSY` if any exclusive bit is set. Otherwise it enables the standard gate. Disable and is-enabled delegate to standard gate ops.

### State, Persistence, And Dependencies
State persists in the target gate register. The wrapper stores the exclusivity mask and uses `imx_ccm_lock`. It depends on the caller correctly describing all mutually exclusive bits.

### Integration Points
Used for clock alternatives that share hardware and must not be active at the same time.

### Risks
The exclusivity read is outside the standard gate lock, so another gate can race between check and enable. Passing zero mask is rejected. Error cleanup frees `gate` rather than the outer allocation pointer, which is equivalent because it is the first member but fragile style.

### Test Signals
Enable competing gates and verify `-EBUSY`, run concurrent enable tests, and check exclusive mask definitions against reference manuals.
