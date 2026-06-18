# sources/distributed-fs/ceph-client/drivers/clk/meson/gxbb-aoclk.c

## Purpose
Implements the Amlogic GXBB always-on clock controller description. The file is a platform-driver wrapper around shared AO clock-controller helpers: it defines the AO register offsets, the AO peripheral gates, the internally generated 32 kHz clock path, CEC and RTC muxes, reset-line numbering, and the sparse clock provider array consumed by the common clock framework.

## Important APIs, Types, And Functions
The central data is a set of `struct clk_regmap` instances using `clk_regmap_gate_ops`, `clk_regmap_gate_ro_ops`, `clk_regmap_mux_ops`, `clk_regmap_mux_ro_ops`, and `meson_clk_dualdiv_ops`. `GXBB_AO_PCLK` expands through `MESON_PCLK` to define simple pclk-derived gate clocks for remote, I2C, UART, and IR blocks. `gxbb_32k_div_table` and `gxbb_ao_32k_div` describe the AO 32 kHz divider programming. `gxbb_ao_reset` maps reset IDs from `dt-bindings/reset/gxbb-aoclkc.h` onto bits in `AO_RTI_GEN_CNTL_REG0`. `gxbb_ao_hw_clks` maps `dt-bindings/clock/gxbb-aoclkc.h` clock IDs to CCF hardware objects. The platform driver uses `meson_aoclkc_probe`.

## Control Flow
There is no custom runtime algorithm in this file. On OF platform-device match for `amlogic,meson-gx-aoclkc`, the driver passes `gxbb_ao_clkc_data.clkc_data` to `meson_aoclkc_probe`. The shared probe registers all clocks through the Meson clock utilities and then registers a reset controller using the reset metadata embedded in `struct meson_aoclk_data`.

## State And Persistence
State is the AO syscon register block reached through the parent syscon node. Clock state is persisted in AO register bits for gates, muxes, dividers, and reset pulses. The 32 kHz path can select external 32 kHz inputs or the internally divided oscillator. The driver keeps no private persistent software state beyond devm-managed registration objects in the shared probe.

## Dependencies And Integration Points
Depends on `meson-aoclk.h`, `meson-clkc-utils.h`, `clk-regmap.h`, `clk-dualdiv.h`, Linux platform driver/module infrastructure, DT clock and reset binding headers, and parent firmware clock names such as `xtal`, `mpeg-clk`, and `ext-32k-*`. Consumers use the AO clock provider IDs and reset provider IDs from Devicetree. The fake CEC parent named `fixme` is an integration workaround for CCF parent probing behavior when the hardware boots with an unknown mux input.

## Risks And Edge Cases
The clock table is sparse and must stay aligned with binding IDs. Parent names are firmware ABI, so DTS names must match. The CEC mux intentionally includes a non-existent parent to force parent discovery; removing it can make boot-time mux state invisible. Reset bits are pulse-style writes handled by the shared AO reset helper, so the bit mapping is high risk. `CLK_IGNORE_UNUSED` keeps historical AO gates on and may hide missing consumers.

## Test Signals
Build with `CONFIG_COMMON_CLK_MESON` and this driver enabled. Boot a GXBB/GXL-family board with `amlogic,meson-gx-aoclkc`; verify clocks appear in `/sys/kernel/debug/clk/clk_summary`, AO UART/I2C/IR/CEC clients can acquire clocks, reset phandles pulse the expected hardware, and CEC/RTC 32 kHz rates resolve correctly for internal and external 32 kHz parent configurations.
