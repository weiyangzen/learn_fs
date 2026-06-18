# sources/distributed-fs/ceph-client/drivers/media/pci/pt1/Kconfig

Purpose: Defines the `DVB_PT1` build option for Earthsoft PT1/PT2 PCI DVB cards.

Important APIs, types, and functions: `config DVB_PT1` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It autoselects `DVB_TC90522`, `DVB_PLL`, and `MEDIA_TUNER_QM1D1B0004` when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

Control flow: Build-time only. Enabling the option builds the `earth-pt1` module/object through the local Makefile.

State and persistence: No runtime state. The option persists in kernel configuration.

Dependencies and integration points: The selected frontend/tuner dependencies match the module-probed demod and tuner devices used by `pt1.c`: TC90522 demods, QM1D1B0004 satellite tuners, and DVB PLL terrestrial tuners.

Risks: With subdriver autoselect disabled, missing demod/tuner modules cause probe-time frontend attachment failures. The help text explains the lack of MPEG decoder and requirement for software decode.

Test signals: Kconfig build tests for module and built-in, dependency rejection without DVB core/PCI/I2C, and autoselect coverage for all `dvb_module_probe()` names used in `pt1.c`.
