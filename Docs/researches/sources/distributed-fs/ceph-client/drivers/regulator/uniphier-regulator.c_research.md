<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/uniphier-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/uniphier-regulator.c

Purpose: Implements UniPhier USB3 VBUS regulator control using memory-mapped registers, clocks, and resets for several Socionext SoC variants.

Important APIs and types: `struct uniphier_regulator_soc_data` describes required clock/reset names, regulator descriptor, and regmap config. `struct uniphier_regulator_priv` stores bulk clocks, reset controls, and selected SoC data. Regulator ops use regmap enable/disable/is_enabled helpers only.

Control flow: Probe allocates private state, obtains match data, maps the MMIO resource, gets required clocks and shared resets, enables clocks, deasserts resets, initializes an MMIO regmap, reads OF regulator init data, and registers the `vbus` regulator. Error paths assert any deasserted resets and disable clocks. Remove asserts all resets and disables clocks.

State and persistence: Runtime state tracks acquired clocks/resets and match data. Regulator state is the USB3 VBUS control register, with enable values writing both the regulator control bit and enable bit.

Dependencies and integration points: Depends on OF compatibles for Pro4/Pro5/PXS2/LD20/PXS3/NX1, platform MMIO resources, common clock/reset frameworks, regmap MMIO, and regulator consumers for USB VBUS.

Risks: Reset and clock lifetime are tied to regulator device lifetime rather than individual enable state, so the MMIO block remains powered while the platform device is bound. Shared resets may be affected by other USB controller users. Register semantics require preserving the regulator-enable bit while disabling output.

Test signals: Probe each compatible, missing clocks/resets, reset deassert failure unwind, enable/disable register values, remove cleanup, and USB host/device consumers toggling VBUS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/uniphier-regulator.c -->
