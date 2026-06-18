# sources/distributed-fs/ceph-client/drivers/regulator/mt6360-regulator.c

Purpose: implements the MediaTek/Richtek MT6360 PMIC regulator platform driver for two bucks and six LDOs, including fault-event IRQ notification.

Important APIs/types/functions: `struct mt6360_regulator_desc` wraps a `regulator_desc` with mode/status registers and per-rail IRQ tables. `mt6360_regulator_ops` provides linear-range voltage listing, regmap enable/disable, selector get/set, status, and mode callbacks. Event handlers `mt6360_pgb_event_handler()`, `mt6360_oc_event_handler()`, `mt6360_ov_event_handler()`, and `mt6360_uv_event_handler()` translate named IRQs to regulator notifier events. `MT6360_REGULATOR_DESC` encodes rail metadata, supply names, DT names, voltage ranges, and off-on delay.

Control flow: probe allocates private state, obtains the parent regmap, then registers each descriptor with `config.dev` set to the parent and `config.regmap` set to the MFD regmap. After each regulator is registered, `mt6360_regulator_irq_register()` looks up every named platform IRQ for that rail and requests a threaded handler. Runtime mode mapping accepts NORMAL, LP/IDLE, and ULP/STANDBY; status reads a per-rail state bit.

State and persistence: all meaningful state lives in hardware registers for enable, selector, mode, and state. The driver keeps only static descriptor tables and the parent regmap pointer. IRQ handlers do not latch local state; they emit notifications from hardware events.

Dependencies and integration: depends on the parent MT6360 MFD exposing a regmap and named interrupts such as `buck1_oc_evt` and `ldo5_pgb_evt`; DT regulator nodes are under the singular `regulator` container and use `mediatek,mt6360-regulator` binding constants for modes.

Risks and test signals: probe fails if any named IRQ is absent, so platform IRQ naming is part of the ABI. `mt6360_regulator_get_mode()` and status callbacks return regmap errors through unsigned/int regulator callback conventions. The LDO voltage ranges have many repeated plateau selectors, so selector-to-voltage coverage matters. Test each IRQ-to-event mapping, missing IRQ handling, buck and LDO mode writes, status-bit reads, off-on delay for LDO3/LDO5, and DT initial/allowed modes.
