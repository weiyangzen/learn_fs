## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2002.c`

Purpose: SG2002-specific CV18xx-family pinctrl data provider. It supplies a smaller/reshaped pin table and condensed power-domain model while reusing the same shared CV18xx ops and electrical conversion style as CV1812H/SG2000.

Important APIs/types/functions: `SG2002_POWER_DOMAIN` defines five domains: MIPI, USB/PLL/ETH, RTC, SD0/eMMC, and SD1. `sg2002_get_pull_up()`, `sg2002_get_pull_down()`, `sg2002_get_oc_map()`, and `sg2002_get_schmitt_map()` provide VDDIO maps for 1.8V-only, 1.8V/3.3V, and Ethernet IO types. `sg2002_pins[]` lists pins in binding order, while `sg2002_pin_data[]` maps each to mux/conf offsets across `sys` and `rtc`. `sg2002_pindata` plugs those arrays into `cv1800_cfg_ops`, `cv1800_pctrl_ops`, `cv1800_pmx_ops`, and `cv1800_pconf_ops`.

Control flow: OF compatible `sophgo,sg2002-pinctrl` selects `sg2002_pindata`; the common Sophgo probe and CV18xx callbacks do all parsing and register programming. The SoC callbacks are used only when generic pinconf needs typical pull resistance, output-current map, or Schmitt threshold conversion.

State and persistence: this file has static immutable tables. The shared runtime keeps per-domain voltage selections in `power_cfg[]`; because SG2002 merges several rails into broad domains, a board DT conflict in one functional area can affect other pins in the same logical domain. MMIO writes made by common ops persist until overwritten or reset.

Dependencies and integration: depends on SG2002 DT binding IDs, the CV18xx shared header, and Linux pinctrl/platform infrastructure. Risks include condensed domain modeling rejecting mixed-voltage configurations, generated offset mistakes, unsupported audio pinconf, and power-source omission causing DT map failures. Test signals include probe on `sophgo,sg2002-pinctrl`, group validation for SD0/eMMC sharing, mux2 tests for MIPI RX pins, Ethernet drive-strength reads, and negative tests for invalid `power-source` or mux values.
