# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-rpgate.c

## Purpose
This file is the SG2042 RP subsystem gate driver. It exposes individual gates for 32 RXU clocks and 16 MP clocks under the `sophgo,sg2042-rpgate` compatible.

## Important APIs, Types, And Functions
`struct sg2042_rpgate_clock` describes a gate clock ID, init data, enable register offset, and bit index. The `SG2042_GATE_FW()` macro declares firmware-parented gates. `sg2042_clk_register_rpgates()` registers each gate with `devm_clk_hw_register_gate_parent_data()`. `sg2042_rpgate_probe()` allocates onecell storage, maps registers, registers gates, and adds the OF provider.

## Control Flow
Probe maps the SYS_CTRL gate resource, then loops over the static `sg2042_gate_rp[]` table. Every entry uses parent name `rpgate`, which is expected to come from the clock generator. RXU gates share `R_RP_RXU_CLK_ENABLE` with distinct bits. MP gates use per-core control registers with bit 0 and are marked `CLK_IS_CRITICAL`.

## State And Persistence
Gate state persists in SYS_CTRL RP gate registers. Runtime state is limited to devm-managed onecell data and MMIO base. A shared spinlock serializes gate writes through the generic gate helper.

## Dependencies And Integration Points
The driver depends on dt-binding IDs from `sophgo,sg2042-rpgate.h`, the shared `sg2042_clk_data` struct, and the upstream `rpgate` parent clock from SG2042 CLKGEN. It integrates with CCF generic gates and Device Tree clock providers.

## Risks
All gates depend on the firmware parent name `rpgate`; naming mismatch prevents parent resolution. MP clocks are critical and therefore resistant to unused-clock cleanup, which is appropriate for processors but should match actual hardware bring-up needs. The file defines status register offsets but does not use them, so gate enable does not verify hardware acknowledgement.

## Test Signals
Boot SG2042 with RP gate node and inspect all RXU/MP gates in `clk_summary`. Verify non-critical RXU gates can be toggled safely and MP gates remain enabled. Confirm parent resolution to the SG2042 clock generator.
