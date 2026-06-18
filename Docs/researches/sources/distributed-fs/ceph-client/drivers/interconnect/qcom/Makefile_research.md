# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Makefile

Purpose: build map for Qualcomm common helpers, BCM voter, RPMh topologies, SMD RPM topologies, OSM L3, and legacy RPM helper bundle.

Important APIs/types/functions: `interconnect_qcom-y := icc-common.o`, `icc-bcm-voter-objs := bcm-voter.o`, `icc-smd-rpm-objs := smd-rpm.o icc-rpm.o icc-rpm-clocks.o`, and many `qnoc-*-objs` definitions.

Control flow: `obj-$(CONFIG_...)` lines build selected helper/topology modules.

State and persistence: no runtime state; controls module composition.

Dependencies/integration: consumes Qualcomm Kconfig symbols and provides platform driver modules.

Risks and test signals: ensure every Kconfig symbol has matching object definitions. `icc-rpmh-obj` is singular rather than `icc-rpmh-objs`; verify direct `icc-rpmh.o` build is intended.
