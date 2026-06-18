# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Makefile

Purpose: kbuild object mapping for Qualcomm PM-domain drivers.

Important rules: `CONFIG_QCOM_CPR` builds `cpr.o`, `CONFIG_QCOM_RPMPD` builds `rpmpd.o`, and `CONFIG_QCOM_RPMHPD` builds `rpmhpd.o`.

Control flow: kbuild includes each object according to the Kconfig tristate value, so modules or built-ins follow the selected config.

State and dependencies: no runtime state. It relies on Kconfig dependencies to provide OPP, regmap, RPMh, command DB, SMD RPM, OF, and genpd symbols.

Risks: object names must stay synchronized with source files and Kconfig symbols. No special flags are present, so compile failures come from driver dependencies rather than this file.

Test signals: run allmodconfig and targeted QCOM configs to ensure each object compiles and links as expected.
