# sources/distributed-fs/ceph-client/drivers/regulator/mtk-dvfsrc-regulator.c

Purpose: exposes MediaTek DVFS Resource Collector voltage performance levels as regulator devices for VCORE and, on some SoCs, VSCP.

Important APIs/types/functions: `struct dvfsrc_regulator_pdata` carries a per-compatible descriptor array. `MTK_DVFSRC_VREG` creates table-voltage descriptors using `dvfsrc_vcore_ops`. `dvfsrc_get_cmd()` maps regulator IDs to `MTK_DVFSRC_CMD_VCORE_LEVEL` or `MTK_DVFSRC_CMD_VSCP_LEVEL`. `dvfsrc_set_voltage_sel()` calls `mtk_dvfsrc_send_request()`, and `dvfsrc_get_voltage_sel()` calls `mtk_dvfsrc_query_info()`.

Control flow: probe obtains match data for the SoC, then registers each descriptor in the table. Runtime selector writes do not touch a local regmap; they send a DVFSRC command to the grandparent DVFSRC device. Runtime reads query the same command and return the DVFSRC level selector. Voltage tables differ for MT6873/8192, MT6893, MT8183, MT8195, and MT8196.

State and persistence: the regulator framework stores no voltage state here. DVFSRC firmware/hardware owns the active level, and this driver is a command bridge. Static tables define allowed selector-to-microvolt mapping for consumers.

Dependencies and integration: depends on the MediaTek DVFSRC SoC API, platform-device hierarchy where the regulator device's parent has a DVFSRC parent, regulator OF matching, and compatible match data. It has no enable/disable operations.

Risks and test signals: parent hierarchy assumptions are hard-coded in `to_dvfsrc_dev()`. Selector values are passed directly as DVFSRC levels, so voltage table order must match firmware contracts. Test each compatible's table size and rails, VCORE-only MT8183/MT8196 cases, invalid regulator IDs, DVFSRC request/query error propagation, and consumers that expect enable/is_enabled support.
