# sources/distributed-fs/ceph-client/drivers/reset/reset-imx8mp-audiomix.c

Purpose: auxiliary reset provider for NXP i.MX8MP AudioMix and i.MX8ULP LPAV reset bits.

Important APIs/types/functions: `struct imx8mp_reset_map`, `struct imx8mp_reset_info`, reset maps for i.MX8MP and i.MX8ULP, `imx8mp_audiomix_update()`, `imx8mp_audiomix_reset_get_regmap()`, and `imx8mp_audiomix_reset_probe()`.

Control flow: auxiliary ID selects reset map. Probe initializes controller metadata using the parent OF node, gets a parent regmap if available, otherwise maps the parent OF resource and creates an MMIO regmap. Assert/deassert update mapped bits with per-line active-low handling.

State and persistence: reset bits live in parent block registers; mapping cleanup is devm-managed when a private regmap is created.

Dependencies and integration: auxiliary bus, parent clock/block device, OF address mapping, regmap, dt-bindings reset IDs.

Risks and test signals: fallback `of_iomap()` assumes parent resource layout and registers an explicit iounmap action. Test both auxiliary IDs, parent-regmap and fallback-regmap paths, active-low lines, and probe cleanup.
