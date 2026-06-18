# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Kconfig

Purpose: Defines the `DVB_PT3` build option for Earthsoft PT3 PCIe DVB cards.

Important APIs, types, and functions: `config DVB_PT3` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It autoselects `DVB_TC90522`, `MEDIA_TUNER_QM1D1C0042`, and `MEDIA_TUNER_MXL301RF` when media subdriver autoselection is enabled.

Control flow: Build-time only. Enabling the option builds the composite `earth-pt3` driver.

State and persistence: No runtime state.

Dependencies and integration points: Dependency selections match the module-probed TC90522 demods plus satellite and terrestrial tuners used by PT3.

Risks: Manual dependency selection is needed if `MEDIA_SUBDRV_AUTOSELECT` is off. The option depends on I2C because PT3 exposes a custom I2C adapter implemented in `pt3_i2c.c`.

Test signals: Kconfig coverage should build `DVB_PT3` as module and built-in, verify dependency rejection, and confirm all module probe names in `pt3.c` are covered by autoselect.
