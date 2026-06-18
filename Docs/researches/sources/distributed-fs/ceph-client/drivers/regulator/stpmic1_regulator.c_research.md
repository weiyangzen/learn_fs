<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c

Purpose: implements regulator support for STPMIC1 PMICs, covering four bucks, six LDOs, VREF_DDR, boost, VBUS_OTG switch, and SW_OUT switch. It also supports buck operating modes, LDO3 bypass, pull-down control, over-current protection configuration, mask-reset behavior, and over-current IRQ notifications.

Important APIs/types/functions: `struct stpmic1_regulator_cfg` wraps a regulator descriptor plus mask-reset and over-current registers/masks. Descriptor macros `REG_BUCK`, `REG_LDO`, `REG_LDO3`, `REG_LDO4`, `REG_VREF_DDR`, `REG_BOOST`, `REG_VBUS_OTG`, and `REG_SW_OUT` build the static `stpmic1_regulator_cfgs[]`. `stpmic1_map_mode()`, `stpmic1_set_mode()`, and `stpmic1_get_mode()` translate buck normal/standby mode. `stpmic1_set_icc()` enables switch-off-on-over-current protection. `stpmic1_regulator_register()` registers one regulator, applies `st,mask-reset`, and requests optional over-current IRQs.

Control flow: probe matches DT regulator child nodes with `of_regulator_match()`, then registers every configured regulator ID. Each registration uses the parent `struct stpmic1` regmap, descriptor/init data/OF node from the match table, and configuration pointer as driver data. Optional `st,mask-reset` sets a PMIC mask-reset bit. If the child node provides an IRQ, the driver requests a shared threaded handler that emits `REGULATOR_EVENT_OVER_CURRENT`.

State and persistence: no dynamic per-regulator state is allocated here beyond regulator devices and IRQ registrations. Hardware registers hold voltage, enable, mode, bypass, pull-down, active-discharge, mask-reset, and OCP state. Mask-reset and OCP settings are persistent only according to PMIC hardware behavior.

Dependencies and integration: depends on STPMIC1 MFD parent, `<dt-bindings/mfd/st,stpmic1.h>`, OF regulator child names such as `buck1`, `ldo3`, `boost`, and `pwr_sw1`, regmap, regulator core, and OF IRQs.

Risks and test signals: `stpmic1_get_mode()` ignores `regmap_read()` errors, so bus failures can be misreported as normal mode. `stpmic1_set_icc()` only supports enabling protection with severity `REGULATOR_SEVERITY_PROT`, not programmable limits or warnings. Probe registers all static entries even if a match lacks init data, which relies on regulator core handling. Test every voltage range including LDO3 DDR-mode selector, bypass, buck mode mapping, pull-down, active discharge on switches, `st,mask-reset`, optional IRQ notification, and parent regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stpmic1_regulator.c -->
