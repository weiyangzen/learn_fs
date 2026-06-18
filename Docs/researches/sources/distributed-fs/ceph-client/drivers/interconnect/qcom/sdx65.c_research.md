# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx65.c

Purpose: provides static RPMh interconnect topology for Qualcomm SDX65. It is very close in shape to SDX55 but updates widths, node sets, BCM grouping, and dt-binding names for SDX65 hardware. The providers are `qcom,sdx65-mc-virt`, `qcom,sdx65-mem-noc`, and `qcom,sdx65-system-noc`.

Important APIs/types/functions: defines about 55 `qcom_icc_node` objects, 20 `qcom_icc_bcm` groups, and three `qcom_icc_desc` descriptors. Important nodes include memory paths (`llcc_mc`, `ebi`, `qns_llcc`), system NoC aggregators (`qnm_aggre_noc`, `qnm_snoc_gc`), and peripheral/config targets for IPA, PCIe, QDSS, SDCC, USB3, BLSP, QPIC, AOSS, DDRSS, and MSS. The driver uses the common `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove` functions with `icc_sync_state`.

Control flow: OF match data selects a descriptor, the common RPMh probe consumes that descriptor, and interconnect consumers request paths by dt-binding IDs. The node graph links masters to intermediate slaves and final targets; BCM arrays determine which RPMh resources receive aggregated votes. Module load and unload are handled by `module_platform_driver`.

State and persistence behavior: local data is static; no file-local locks, allocations, or persistence exist. Runtime bandwidth aggregation and BCM vote state are maintained by the shared Qualcomm RPMh interconnect layer. Keepalive BCMs (`MC0`, `PN0`, `SH0`, `SN0`) preserve essential memory/system paths.

Dependencies and integration points: includes `dt-bindings/interconnect/qcom,sdx65.h`, `bcm-voter.h`, and `icc-rpmh.h`. The file depends on device-tree providers matching its three compatible strings and on subsystem consumers using the same master/slave IDs. It integrates with RPMh firmware and the interconnect core rather than touching hardware registers directly.

Risks: most bugs would be incorrect hardware modeling. SDX65 changes relative to SDX55 include narrower/wider bus widths in several memory/system links and a large `PN0` BCM that keeps many config/system nodes alive; errors there can affect idle power or boot stability. Missing links in high-fanout nodes such as `qnm_aggre_noc`, `qnm_ipa`, or `qnm_memnoc` can strand consumers. Because there is no procedural validation, array indices must match the dt-binding enum exactly.

Test signals: compile coverage catches symbol and binding drift. Runtime validation should confirm all three providers probe, interconnect debugfs shows expected nodes and links, and bandwidth votes change under IPA, PCIe, USB3, SDCC, QDSS, and memory stress. Device-tree schema checks should verify compatible strings and provider references.
