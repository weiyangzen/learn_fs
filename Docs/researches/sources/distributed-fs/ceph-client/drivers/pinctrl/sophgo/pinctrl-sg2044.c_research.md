## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2044.c`

Purpose: SG2044-specific data provider for the SG2042-style pinctrl ops. It supplies SG2044 binding IDs, pin names, register offsets, flags, electrical pull values, output-current map, and the `sophgo,sg2044-pinctrl` platform binding.

Important APIs/types/functions: `sg2044_get_pull_up()` returns 19500 ohms, `sg2044_get_pull_down()` returns 23200 ohms, and `sg2044_oc_map[]` provides 16 drive-current steps from 3200 to 51400 microamps through `sg2044_get_oc_map()`. `sg2044_pins[]` includes SMBus sideband pins, PCIe lanes 0-4, SPI flash, eMMC/SDIO, RGMII, PWM/FAN, I2C, UART, SPI, JTAG0-3, GPIO0-31, boot/mode straps, socket IDs, multiple DDR clock inputs, test pins, and BISR. `sg2044_pin_data[]` maps these to SG2042-style offsets and flags. `sg2044_pindata` reuses `sg2042_cfg_ops`, `sg2042_pctrl_ops`, `sg2042_pmx_ops`, and `sg2042_pconf_ops`.

Control flow: OF match `sophgo,sg2044-pinctrl` selects this data, then the shared Sophgo probe and SG2042 ops handle mapping, DT group parsing, mux, and pinconf. This file participates at runtime only through VDDIO callbacks and table lookups.

State and persistence: tables are immutable. Runtime state is in the single SG2044 pinctrl MMIO region. Offset/flag data determines which 16-bit halfword is touched and whether mux/output-enable operations are suppressed.

Dependencies and integration: depends on `dt-bindings/pinctrl/pinctrl-sg2044.h` and the SG2042-family shared header/ops. Risks include copied SG2042 assumptions not matching SG2044 hardware, lack of mux-value validation in shared SG2042 ops, no `PIN_FLAG_ONLY_ONE_PULL` use where hardware might need it, and register-offset drift because the SG2044 table has different layout from SG2042. Test signals include matching `sophgo,sg2044-pinctrl`, pinconf on low/high pairs, strap pins preserving no-mux/no-output-enable behavior, drive map boundary tests, and debugfs pin reports matching expected register offsets.
