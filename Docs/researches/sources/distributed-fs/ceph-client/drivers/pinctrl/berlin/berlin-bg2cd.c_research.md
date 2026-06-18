# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2cd.c

Purpose: Berlin BG2CD descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: `berlin2cd_soc_pinctrl_groups`, `berlin2cd_sysmgr_pinctrl_groups`, `berlin2cd_pinctrl_match`, and `berlin2cd_pinctrl_probe()` provide BG2CD-specific data to the shared Berlin core.

Control flow: builtin platform driver matches `marvell,berlin2cd-soc-pinctrl` or `marvell,berlin2cd-system-pinctrl`; probe passes the selected descriptor to `berlin_pinctrl_probe()`, which obtains the parent syscon regmap and registers pinctrl.

State and persistence: descriptor-only source; mux selections persist in syscon registers. Unknown groups are represented with empty function descriptors and therefore are not exposed as selectable functions.

Dependencies/integration: Linux OF/platform/property helpers and `berlin.h`. Exposes groups for JTAG, GPIO, SD0, USB debug, front-end, PLL, PWM, UART, EDDC, TWSI, SPI, NAND, and other BG2CD muxes.

Risks: many system-manager groups are unknown placeholders; attempting to use them from DT will not resolve a function. Common core function synthesis depends on null-terminated function arrays emitted by macros.

Test signals: compile with `MACH_BERLIN_BG2CD`, verify both compatibles bind, check unknown groups do not create bogus functions, and use debugfs to confirm G/GSM group names and function membership.
