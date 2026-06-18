## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2000.c`

Purpose: SoC-specific pin table and electrical map provider for Sophgo SG2000 pinctrl. It is structurally aligned with CV1812H, using the shared CV18xx implementation and generated vendor pinout definitions under `dt-bindings/pinctrl/pinctrl-sg2000.h`.

Important APIs/types/functions: `sg2000_get_pull_up()`, `sg2000_get_pull_down()`, `sg2000_get_oc_map()`, and `sg2000_get_schmitt_map()` implement VDDIO conversions. The `SG2000_POWER_DOMAIN` enum and `sg2000_power_domain_desc[]` name eight domains including EPHY, MIPI, eMMC, RTC, SD0, SD1, and VIVO. `sg2000_pins[]` lists all visible pinctrl pins, and `sg2000_pin_data[]` maps them to CV18xx mux/conf register descriptors. `sg2000_pindata` connects the SoC data to `cv1800_*` ops.

Control flow: `module_platform_driver()` registers `sg2000_pinctrl_driver`; `sophgo_pinctrl_probe()` receives `sg2000_pindata` from the OF match. Runtime parsing, mux setting, and pinconf handling are delegated to `pinctrl-cv18xx.c`, which calls SG2000 VDDIO callbacks when converting generic pinconf arguments.

State and persistence: compile-time tables are immutable. Runtime state is shared CV18xx state: per-power-domain voltage choices are stored once in `power_cfg[]`, and register writes persist in the SoC pinmux/pinconf MMIO blocks.

Dependencies and integration: depends on the CV18xx header and common Sophgo backend, Linux module/platform/of/pinctrl APIs, and SG2000 binding constants. The table includes pins with `IO_TYPE_AUDIO` and `IO_TYPE_ETH`, which mux normally but reject generic CV18xx pinconf. Risks include generated-table drift, wrong domain voltage maps, cross-domain grouping rejected by common validation, and inconsistent binding IDs. Test signals include DT compatible match `sophgo,sg2000-pinctrl`, successful mux on representative camera/MIPI/SD/eMMC/RTC pins, rejected invalid mux2 encodings, voltage conflict tests, and pinconf conversion tests over both 1.8V and 3.3V domains.
