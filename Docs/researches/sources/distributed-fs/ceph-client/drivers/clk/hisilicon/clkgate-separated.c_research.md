## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkgate-separated.c

### Purpose
`clkgate-separated.c` implements Hisilicon gates whose enable, disable, and status registers are separated by fixed offsets.

### Important APIs, Types, And Functions
`struct clkgate_separated` stores `clk_hw`, enable base, bit index, flags, and lock. `clkgate_separated_enable()`, `clkgate_separated_disable()`, and `clkgate_separated_is_enabled()` implement CCF ops. `hisi_register_clkgate_sep()` constructs and registers the clock.

### Control Flow
Enable writes `BIT(bit_idx)` to the enable register, then reads status to flush/observe the operation. Disable writes the bit to the disable register at `+0x4`, then reads status at `+0x8`. Both paths take the optional shared spinlock.

### State, Persistence, And Dependencies
Gate state persists in hardware status bits. Driver state is heap allocated and tied to the registered clock. It depends on relaxed MMIO access, CCF registration, and hardware using the fixed enable/disable/status layout.

### Integration Points
Hi6220, Hi3670, and other Hisilicon SoC tables register separated gates through `hisi_clk_register_gate_sep()`.

### Risks
`clk_gate_flags` is stored but not used by the ops, so polarity flags do not affect behavior. There is no normal unregister/free callback. Incorrect register base offsets can write enable/disable commands into unrelated registers.

### Test Signals
Toggle representative separated gates and confirm status readback, verify paired enable/disable register offsets on each SoC, and test concurrent gate operations under the shared lock.
