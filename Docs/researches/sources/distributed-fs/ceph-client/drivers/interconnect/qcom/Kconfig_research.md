# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Kconfig

Purpose: Kconfig menu for Qualcomm interconnect drivers across RPMh, SMD RPM, BCM voter, OSM L3, and many SoC topology modules.

Important APIs/types/functions: shared symbols include `INTERCONNECT_QCOM`, `INTERCONNECT_QCOM_BCM_VOTER`, `INTERCONNECT_QCOM_RPMH_POSSIBLE`, `INTERCONNECT_QCOM_RPMH`, and `INTERCONNECT_QCOM_SMD_RPM`.

Control flow: SoC symbols select RPMh or SMD RPM helpers and BCM voter where needed. `INTERCONNECT_QCOM_RPMH_POSSIBLE` guards build/link combinations involving RPMh and command DB.

State and persistence: `.config` state controls driver availability.

Dependencies/integration: Qualcomm RPMh, command DB, SMD RPM, OF, architecture config.

Risks and test signals: test module/built-in matrices, COMPILE_TEST combinations, and every new SoC symbol for correct helper selection. Watch for dependency drift causing unresolved symbols.
