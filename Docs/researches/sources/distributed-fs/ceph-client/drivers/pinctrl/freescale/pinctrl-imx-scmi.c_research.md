# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx-scmi.c

Purpose: Implements an i.MX pinctrl driver that delegates mux/config programming to SCMI firmware using the SCMI pinctrl protocol, currently allowlisted for i.MX94, i.MX95, and i.MX952.

Important APIs and functions: `struct scmi_pinctrl_imx` stores SCMI handles, protocol ops, and the pinctrl descriptor. `pinctrl_scmi_imx_dt_node_to_map()` converts `fsl,pins` cells into packed SCMI config maps. Pinconf callbacks call `settings_get_one()` and `settings_conf()`. `scmi_pinctrl_imx_get_pins()` queries firmware pin names, and `scmi_pinctrl_imx_probe()` registers/enables the controller.

Control flow: SCMI core matches `SCMI_PROTOCOL_PINCTRL`. Probe checks machine compatibility, obtains protocol ops, queries pin count/names, registers pinctrl, and enables hogs. DT map parsing emits one `PIN_MAP_TYPE_CONFIGS_PIN` per pin, combining mux, optional extended mux, pad config, and daisy selection into one firmware call. Pinmux `set_mux` intentionally does nothing because mux is applied through pinconf.

State and persistence: Driver state persists in the SCMI device allocation. Generated map configs are heap-copied arrays referenced by pinctrl maps; firmware-applied settings persist in platform firmware/hardware until changed or reset.

Dependencies and integration points: Depends on SCMI protocol APIs, OF machine compatibility, generic pinctrl groups/functions, generic pinconf packing, and i.MX `fsl,pins` binding cell layout.

Risks: Daisy offset is a static cached value derived from machine compatibility, so multi-SoC test environments need care. Map free only releases the map array, while per-pin copied config arrays need ownership scrutiny. The source as read also contains an apparent duplicate local declaration in `pinctrl_scmi_imx_pinconf_set()`, which build coverage should catch. Firmware error translation and maximum config count are critical.

Test signals: Build with `CONFIG_PINCTRL_IMX_SCMI`, probe on allowlisted i.MX9 boards, SCMI firmware pin count/name queries, DT states with mux/config/daisy/ext fields, suspend/resume consumers, and firmware error injection for unsupported settings.
