# sources/distributed-fs/ceph-client/drivers/regulator/mt6370-regulator.c

Purpose: implements the MT6370 regulator subdriver for display bias boost/output rails and a vibrator LDO, with fault reporting and optional external GPIO enable control.

Important APIs/types/functions: `struct mt6370_priv` stores the device, regmap, registered rdevs, and whether external control has been requested. `mt6370_regulator_descs[]` describes `dsvbst`, `dsvpos`, `dsvneg`, and `vibldo`. Ops sets `mt6370_dbvboost_ops`, `mt6370_dbvout_ops`, and `mt6370_ldo_ops` expose selector, enable, bypass, active discharge, ramp, and error-flag callbacks. `mt6370_of_parse_cb()` attaches optional enable GPIOs and enables PMIC external-control mode.

Control flow: probe obtains the parent regmap, registers all four regulators, stores rdev pointers, then requests six named platform IRQs for SCP/OCP events. Runtime error flags read `MT6370_REG_DB_STAT` or `MT6370_REG_LDO_STAT` and map bits to `REGULATOR_ERROR_UNDER_VOLTAGE` or `REGULATOR_ERROR_OVER_CURRENT`. IRQ handlers emit regulator notifier events for the affected rdev.

State and persistence: hardware owns voltage selectors, bypass state, enable state, active discharge bits, ramp settings, fault status, and external-control enable. Driver state tracks whether any output rail uses an enable GPIO; when the first GPIO is found it sets `use_external_ctrl` after assigning the GPIO, while the next external rail may actually set `MT6370_DBEXTEN_MASK`.

Dependencies and integration: depends on parent regmap, platform IRQ names, regulator OF children under `regulators`, optional `enable-gpios`, and regulator core support for `ena_gpiod`. The display-bias outputs share external-control semantics.

Risks and test signals: `platform_get_irq_byname()` return values are not checked before `devm_request_threaded_irq()`. External-control enabling depends on registration order and only happens after `priv->use_external_ctrl` was already true from a previous parse. Fault status bits may be sticky, so error reporting should be validated against hardware clear behavior. Test GPIO/no-GPIO combinations, both display output rails with external pins, all named IRQs, bypass on boost, active discharge for outputs and LDO, ramp tables, and `get_error_flags()` bit mapping.
