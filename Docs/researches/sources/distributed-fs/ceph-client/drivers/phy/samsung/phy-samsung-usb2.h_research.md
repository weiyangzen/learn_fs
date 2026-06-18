# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.h

Purpose: shared interface and data model for the Samsung USB2 PHY core and its SoC-specific configuration files.

Important APIs, types, and functions: defines `KHZ`/`MHZ`; forward declarations; `struct samsung_usb2_phy_instance`, `struct samsung_usb2_phy_driver`, `struct samsung_usb2_common_phy`, and `struct samsung_usb2_phy_config`; extern declarations for Exynos and S5PV210 config tables. The common PHY object carries per-instance callbacks, ID, and label; the config table carries the PHY array, reference-rate conversion callback, number of PHYs, and feature flags.

Control flow: the header itself has no executable flow, but it defines how the core driver discovers per-instance behavior. `samsung_usb2_phy_probe()` consumes `num_phys`, `phys`, `has_mode_switch`, `has_refclk_sel`, and `rate_to_clk`; power operations consume the instance callbacks.

State and persistence: `struct samsung_usb2_phy_driver` owns all mutable runtime state: clock/regulator handles, MMIO base, PMU/sysreg regmaps, cached reference clock values, lock, and flexible instance array. `struct samsung_usb2_phy_instance` keeps counters (`int_cnt`, `ext_cnt`) that SoC-specific code can use for shared internal/external PHY users.

Dependencies and integration points: includes Linux clock, generic PHY, device, regmap, spinlock, and regulator APIs. The extern config symbols are supplied by companion Samsung PHY implementation files selected by Kconfig.

Risks: ABI is internal but tightly shared across several SoC files; changing field semantics can break callbacks. `label` is mutable `char *` although tables likely hold string literals. The shared counters are not manipulated by the core file, so correctness depends on callback discipline and locking.

Test signals: compile all Samsung USB2 PHY variants together and individually; static analysis for missing config symbols under Kconfig combinations; runtime tests that exercise callbacks relying on `int_cnt`, `ext_cnt`, `has_mode_switch`, and `has_refclk_sel`.
