# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Kconfig

Purpose: defines Qualcomm PM-domain driver configuration entries.

Important entries: `QCOM_CPR` enables Core Power Reduction support for Qualcomm SoCs such as QCS404, depends on QCOM/COMPILE_TEST plus I/O memory, and selects OPP and regmap. `QCOM_RPMHPD` enables RPMh power-domain support with performance states, requiring `QCOM_RPMH` and command DB. `QCOM_RPMPD` enables legacy RPM SMD power domains, requiring PM, OF, and `QCOM_SMD_RPM`, and selecting genpd OF support.

Control flow and integration: these symbols map to `cpr.o`, `rpmhpd.o`, and `rpmpd.o` in the local Makefile. They control whether voltage/performance-state providers are available for Qualcomm DT power-domain consumers.

State and persistence behavior: no runtime state; build configuration only.

Dependencies: OPP, regmap, RPMh command DB, SMD RPM, OF, and generic PM domains. Correct operation depends on matching DT bindings in the corresponding drivers.

Risks: help text for `QCOM_CPR` contains a minor `CPUfrequency` typo. Dependency choices mean RPMh and RPM drivers are mutually selected by platform support, not by this file alone; missing command DB/SMD support hides the options.

Test signals: compile with QCOM and COMPILE_TEST configs, verify selected objects build, and boot RPM/RPMh platforms to confirm performance-state providers bind.
