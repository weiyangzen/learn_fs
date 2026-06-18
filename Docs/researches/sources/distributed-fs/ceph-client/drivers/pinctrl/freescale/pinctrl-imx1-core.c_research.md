# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1-core.c

Purpose: Implements the shared pinctrl core for legacy i.MX1/i.MX21/i.MX27-style controllers, whose muxing is organized by ports and bitfields rather than modern IOMUXC pad-control registers.

Important APIs and functions: Exported entry is `imx1_pinctrl_core_probe()`. Internal register helpers are `imx1_write_bit()`, `imx1_write_2bit()`, `imx1_read_bit()`, and `imx1_read_2bit()`. Pinctrl operations include group lookup, DT map generation, mux setting, function enumeration, pullup config get/set, and debug display.

Control flow: SoC files provide pad descriptors and call the core probe. Probe maps MMIO, parses DT child functions/groups from `fsl,pins = <PIN MUX_ID CONFIG>`, registers pinctrl, and populates child devices. State selection maps each group into one mux map plus per-pin config maps. `imx1_pmx_set()` decodes `mux_id` into function/GPIO/direction/output/input bits and writes the corresponding port registers.

State and persistence: `struct imx1_pinctrl` holds device, pinctrl device, MMIO base, and parsed SoC info. Parsed functions/groups and pin arrays are devm allocated into mutable SoC info. Hardware state persists in DDIR, OCR, ICONFA/B, GIUS, GPR, and PUEN registers.

Dependencies and integration points: Depends on OF platform parsing, common pinctrl/pinmux/pinconf APIs, and SoC data from `pinctrl-imx1.c`/`pinctrl-imx27.c`. It also calls `of_platform_populate()` for subdevices under the controller node.

Risks: A static `grp_index` in function parsing can retain value across probes unless only one legacy controller probes. The static `pinctrl_desc` is mutated per probe, which is another multi-instance risk. Register helpers rely on exact port/pin bitfield math. DT config only represents pullup enable.

Test signals: Boot i.MX1 and i.MX27 DTs, parse multiple functions/groups, inspect debugfs register-derived state, test GPIO-vs-function muxing, pullup config changes, and subdevice population under the IOMUXC node.
