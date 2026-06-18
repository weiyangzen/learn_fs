# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.h

## Purpose
This header declares the shared legacy SoCFPGA clock-manager interface. It defines common register offsets, helper macros, global MMIO base symbols, init function prototypes, and simple wrapper structures for PLL, gate, and peripheral clocks.

## Important APIs, Types, And Functions
Constants include `CLKMGR_CTRL`, `CLKMGR_BYPASS`, `CLKMGR_DBCTRL`, `CLKMGR_L4SRC`, `CLKMGR_PERPLL_SRC`, and `SOCFPGA_MAX_PARENTS`. `SYSMGR_SDMMC_CTRL_SET()` and `SYSMGR_SDMMC_CTRL_SET_AS10()` encode SDMMC sample/drive-select fields for system-manager integration.

The header exposes `clk_mgr_base_addr` and `clk_mgr_a10_base_addr`, plus init prototypes for standard and Arria10 PLL, peripheral, and gate clocks. `struct socfpga_pll` wraps `struct clk_gate`; `struct socfpga_gate_clk` and `struct socfpga_periph_clk` carry parent name, fixed divider, optional divider/bypass registers, field widths/shifts, and for gates a `regmap *sys_mgr_base_addr`.

## Control Flow
No executable flow exists in the header. The data structures are consumed by implementation files that parse Device Tree, map registers, construct `clk_hw` instances, and install operations for rate and gate control.

## State And Persistence
The global MMIO bases represent process-wide state set during clock-manager initialization. The per-clock structs store register pointers and bitfield metadata but not persistent policy. Hardware registers hold the effective divider, bypass, and gate state.

## Dependencies And Integration Points
The header depends on `<linux/clk-provider.h>` and implicitly on CCF, MMIO, and regmap users in implementation files. It is shared by legacy SoCFPGA clock declarations in `clk.c` and lower-level clock implementations elsewhere in the directory.

## Risks
Global base-address state can be fragile if multiple compatible controllers or deferred init paths are introduced. Register field metadata is stored as raw offsets/pointers, so incorrect DT parsing or SoC variant selection can lead to wrong MMIO writes. The `streq()` macro hides raw `strcmp()` semantics and assumes non-NULL strings.

## Test Signals
Static build coverage should compile both legacy and Arria10 paths. Runtime tests should validate SDMMC timing register encodings, bypass transitions, and that all legacy OF-declared nodes resolve parent clocks correctly.
