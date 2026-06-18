<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c

Purpose: exposes Delta TN48M CPLD GPI/GPO register blocks through the generic `gpio-regmap` helper.

Important APIs, types, and functions: `enum tn48m_gpio_type` differentiates GPO and GPI blocks. `struct tn48m_gpio_config` describes line count, lines per register, and type. `tn48m_gpio_probe()` builds a `gpio_regmap_config` from match data and a parent regmap.

Control flow: probe checks for a parent device, fetches match data, reads the `reg` property as the register base, obtains the parent's regmap, fills `gpio_regmap_config`, selects either `reg_set_base` for output-only or `reg_dat_base` for input-only, and registers the gpio-regmap device.

State and persistence behavior: no local mutable state is kept. GPIO values live in the parent CPLD regmap registers.

Dependencies and integration points: depends on parent MFD/regmap creation, OF compatibles `delta,tn48m-gpo` and `delta,tn48m-gpi`, and the `gpio/regmap.h` framework.

Risks and test signals: a wrong `reg` property or compatible swaps input/output semantics. There is no direction register, so capabilities are fixed by compatible. Test both GPI and GPO compatibles, parent-regmap absence, `reg` parsing, four-line numbering, and gpio-regmap read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tn48m.c -->
