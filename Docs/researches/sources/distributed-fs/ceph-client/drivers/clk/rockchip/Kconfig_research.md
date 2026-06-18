# sources/distributed-fs/ceph-client/drivers/clk/rockchip/Kconfig

## Purpose
Declares Rockchip common clock controller configuration symbols. `COMMON_CLK_ROCKCHIP` enables shared Rockchip clock infrastructure when `ARCH_ROCKCHIP` is selected. Per-SoC booleans select individual CRU drivers for PX30, RV110x/RV1126 variants, and RK30xx/RK35xx/RK3588 families.

## Important APIs, Types, and Functions
This is Kconfig metadata. Symbols include `CLK_PX30`, `CLK_RV1103B`, `CLK_RV110X`, `CLK_RV1126`, `CLK_RV1126B`, `CLK_RK3036`, `CLK_RK312X`, `CLK_RK3188`, `CLK_RK322X`, `CLK_RK3288`, `CLK_RK3308`, `CLK_RK3328`, `CLK_RK3368`, `CLK_RK3399`, `CLK_RK3506`, `CLK_RK3528`, `CLK_RK3562`, `CLK_RK3568`, `CLK_RK3576`, and `CLK_RK3588`.

## Control Flow, State, and Persistence
No runtime state exists. The config controls which object files are built and which compatible strings can probe at runtime. Most SoC options default to `y` under the common option and constrain architecture to ARM, ARM64, or `COMPILE_TEST`.

## Dependencies, Integration Points, Risks, and Test Signals
The file integrates with the kernel Kconfig system and local Makefile. Risks are enabling an SoC on an unsupported architecture or forgetting Makefile linkage. Test with `allyesconfig`, `COMPILE_TEST`, and per-architecture builds.
