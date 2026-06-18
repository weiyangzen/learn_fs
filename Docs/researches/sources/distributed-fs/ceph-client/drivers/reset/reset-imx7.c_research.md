# sources/distributed-fs/ceph-client/drivers/reset/reset-imx7.c

Purpose: NXP i.MX7/i.MX8M SRC reset controller for SoC reset lines defined in SRC syscon registers.

Important APIs/types/functions: `struct imx7_src_signal`, `struct imx7_src_variant`, `struct imx7_src`, signal tables for i.MX7, i.MX8MQ, and i.MX8MP, variant-specific set/assert/deassert functions, and `imx7_reset_probe()`.

Control flow: OF match selects a variant containing a signal table and ops. Probe resolves the node as a syscon regmap, attaches it to the device, and registers. Reset IDs index signal tables. Variant set functions handle active-low or enable-style bits for PCIe, MIPI DSI, M4/M7, and selected PHY resets; PCIe PHY deassert waits at least 10 us.

State and persistence: SRC register bits hold state; no software cache.

Dependencies and integration: platform bus, OF, syscon/regmap, dt-bindings for i.MX reset IDs, reset framework.

Risks and test signals: active-high/active-low special cases are hardware-sensitive and table-driven. Test all compatible variants, PCIe timing, MIPI/M4 polarity, syscon lookup failure, and consumer DT IDs within `nr_resets`.
