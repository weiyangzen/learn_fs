# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.h

Purpose: Defines the legacy i.MX1/i.MX27 pinctrl data structures shared between SoC table files and `pinctrl-imx1-core.c`.

Important APIs and types: `struct imx1_pin` carries pin ID, encoded mux ID, and config. `struct imx1_pin_group` stores group name, pin IDs, pin array, and count. `struct imx1_pmx_func` maps a function to group names. `struct imx1_pinctrl_soc_info` carries device pointer, static pins, parsed groups/functions, and counts. `IMX_PINCTRL_PIN()` wraps `PINCTRL_PIN()`, and `imx1_pinctrl_core_probe()` is the common probe entry.

Control flow: SoC files initialize static pins and call the core probe. The core fills mutable group/function arrays after parsing DT, then uses them in pinctrl and pinmux callbacks.

State and persistence: The header owns no state, but its structs define driver-lifetime parsed DT state. Hardware register persistence is managed by the core implementation.

Dependencies and integration points: Requires public pinctrl pin descriptor types from includers and platform device declarations. Used by i.MX1 and i.MX27 SoC drivers.

Risks: Encoded mux IDs are opaque bitfields decoded only by the core. Any binding change must preserve the `<PIN MUX_ID CONFIG>` layout or update parser and docs together. Mutable fields in `soc_info` make const-correctness impossible for current users.

Test signals: Build legacy SoC drivers, parse DT functions/groups, and exercise mux/config callbacks using representative mux ID encodings.
