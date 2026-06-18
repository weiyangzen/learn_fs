# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qusb2.c

Purpose: Provides the Qualcomm QUSB2 high-speed USB2 PHY driver. It supports multiple SoCs through per-compatible init tables, register-layout arrays, PLL readiness masks, clock-scheme behavior, and tuning policy.

Important APIs/types/functions: Key types are `struct qusb2_phy_init_tbl`, `struct qusb2_phy_cfg`, `struct override_param(s)`, and `struct qusb2_phy`. The generic PHY contract is `qusb2_phy_gen_ops` with `qusb2_phy_init()`, `qusb2_phy_exit()`, and `qusb2_phy_set_mode()`. Runtime PM uses `qusb2_phy_runtime_suspend()` and `qusb2_phy_runtime_resume()`. Probe parses optional DT override properties and nvmem trim data.

Control flow: Probe maps MMIO, gets `cfg_ahb`, `ref`, optional `iface`, reset, supplies, optional TCSR syscon, optional nvmem cell, and board tuning overrides, then registers one PHY. Init enables regulators and clocks, resets the PHY, disables power, writes the SoC init table, applies DT overrides, applies fused HS TX trim, enables the PHY, resolves single-ended versus differential clock scheme through TCSR/default config, optionally selects `PLL_TEST`, and checks PLL/core-ready status. Exit powers down and unwinds clocks, reset, and regulators. Runtime suspend programs DP/DM wake triggers based on USB line mode, optionally holds PLL reset, toggles autoresume, and disables clocks.

State and persistence: `struct qusb2_phy` stores current mode, clock-scheme choice, initialization flag, override values, optional nvmem/TCSR handles, and resource handles. PHY tuning and PLL state persist in registers until exit, reset, or reinit.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clocks, reset, regulators, nvmem, TCSR regmap/syscon, runtime PM, and `dt-bindings/phy/phy-qcom-qusb2.h`. It is consumed by USB controllers through OF PHY phandles.

Risks: Register layouts differ by SoC, so a wrong `qusb2_phy_cfg` can write valid values to wrong offsets. Optional efuse and DT override values directly affect signal quality. Runtime suspend wake masks depend on accurate `set_mode()` calls from the USB controller. Missing cleanup on init failure can leave clocks or regulators enabled.

Test signals: Build and probe every compatible configuration, validate HS/FS/LS host and device modes, confirm PLL/core-ready status, verify nvmem trim and DT tuning writes with register dumps, test runtime suspend/resume wake for connected and disconnected states, and exercise init failure paths by removing clocks/resets/supplies in DT tests.
