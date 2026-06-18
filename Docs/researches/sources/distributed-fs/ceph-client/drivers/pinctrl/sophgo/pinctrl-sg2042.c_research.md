## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.c`

Purpose: SG2042-specific pin list, table, electrical values, and platform driver binding. It supplies data consumed by the shared SG2042 ops for a broad server-class pin set including LPC, PCIe, SPI flash, eMMC/SDIO, RGMII, PWM/FAN, I2C, UART, SPI, JTAG, GPIO, boot/mode straps, clock inputs, reset, test, and BISR pins.

Important APIs/types/functions: `sg2042_get_pull_up()` and `sg2042_get_pull_down()` return fixed typical pull values of 35k and 28k ohms. `sg2042_oc_map[]` provides 16 output-current steps from 5400 to 45400 microamps via `sg2042_get_oc_map()`. `sg2042_vddio_cfg_ops` exports those conversions. `sg2042_pins[]` lists `PINCTRL_PIN()` descriptors from `dt-bindings/pinctrl/pinctrl-sg2042.h`. `sg2042_pin_data[]` maps every pin to an offset and flags such as `PIN_FLAG_WRITE_HIGH`, `PIN_FLAG_ONLY_ONE_PULL`, `PIN_FLAG_NO_PINMUX`, and `PIN_FLAG_NO_OEX_EN`.

Control flow: the OF match `sophgo,sg2042-pinctrl` selects `sg2042_pindata`, then `sophgo_pinctrl_probe()` registers the shared SG2042 ops. Runtime set-mux and pinconf operations are table-driven by offsets and flags from this file.

State and persistence: immutable pin tables describe register layout; hardware register contents are the only persistent runtime state. Because many adjacent pins share a 32-bit register split into low/high halves, correct `PIN_FLAG_WRITE_HIGH` placement is essential to preserve neighboring pin state.

Dependencies and integration: depends on SG2042 binding constants, `pinctrl-sg2042.h`, and the shared Sophgo/SG2042 ops. Risks are dominated by table correctness and flag semantics: strap/clock/test pins are marked no-mux/no-output-enable, many pins use single-direction pull encoding, and any generated offset error can affect unrelated pins. Test signals include probe with `sophgo,sg2042-pinctrl`, mux/pinconf on low and high halfword pairs, GPIO/pinctrl handoff on PL-style GPIO pins, no mux writes for boot/mode pins, and drive-strength conversion for all 16 map entries.
