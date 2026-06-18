# sources/distributed-fs/ceph-client/drivers/misc/qcom-coincell.c

Purpose: configures the coincell/backup-battery charger block in Qualcomm PMICs through parent regmap registers.

Important APIs and types: `struct qcom_coincell` stores device, regmap, and base address. `qcom_coincell_chgr_config()` validates and writes resistor/voltage/enable settings. `qcom_coincell_probe()` reads DT properties and calls the configurator. Match table supports `qcom,pm8941-coincell`.

Control flow: probe gets the parent regmap, reads `reg` as base address, treats `qcom,charger-disable` as a disable request, otherwise requires `qcom,rset-ohms` and `qcom,vset-millivolts`. The config function disables by writing zero to enable register, or maps exact resistor/voltage values to indices, writes RSET and VSET, then writes enable bit.

State and persistence: no allocated long-lived driver state; the PMIC registers persist until hardware reset or another driver changes them.

Dependencies and integration points: depends on OF, platform bus, parent PMIC regmap, and DT binding values matching hardcoded maps.

Risks and test signals: invalid DT values reject probe. The comment notes voltage encoding differences for some PMICs, so compatible coverage is important. Tests should cover disabled mode, all valid resistor/voltage entries, invalid values, missing properties, regmap write failures, and parent regmap absence.
