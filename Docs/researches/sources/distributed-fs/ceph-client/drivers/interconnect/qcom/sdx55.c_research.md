# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx55.c

Purpose: describes the Qualcomm SDX55 modem-platform interconnect topology for RPMh-managed NoCs. It exposes three providers: `qcom,sdx55-mc-virt`, `qcom,sdx55-mem-noc`, and `qcom,sdx55-system-noc`. The file is mostly static topology data for memory-controller, memory NoC, and system NoC paths used by modem, IPA, PCIe, USB, storage, Ethernet, QDSS, and configuration targets.

Important APIs/types/functions: uses `struct qcom_icc_node` for about 58 nodes, `struct qcom_icc_bcm` for about 20 BCMs, and three `struct qcom_icc_desc` descriptors. Nodes specify names, channels, bus widths, and pointer links. BCMs include keepalive memory/shared paths (`MC0`, `SH0`, `SN0`) plus peripheral/system BCM groups (`PN*`, `SN*`, `CE0`). The platform driver is named `qnoc-sdx55`, uses `qcom_icc_rpmh_probe`/`qcom_icc_rpmh_remove`, exports `MODULE_DEVICE_TABLE(of, qnoc_of_match)`, and uses `icc_sync_state`.

Control flow: the platform bus matches one of the three SDX55 compatibles, passes the selected descriptor to the common RPMh probe, and the common code registers the provider and node graph with the interconnect core. Bandwidth requests from consumers then traverse the graph and vote on the BCM groups declared here. `module_platform_driver` supplies normal module init/exit handling.

State and persistence behavior: the file has no mutable local runtime state and no persistence. Static node and BCM arrays are the authoritative topology. Runtime state is created in common RPMh interconnect code and in RPMh firmware votes. Keepalive BCMs keep memory paths available even before or after consumer votes converge.

Dependencies and integration points: includes `dt-bindings/interconnect/qcom,sdx55.h`, `bcm-voter.h`, and `icc-rpmh.h`. It integrates with SDX55 device trees, the Linux interconnect framework, RPMh BCM voting, and subsystem drivers that request paths for PCIe, IPA, USB3, SDCC, QPIC, BLSP, QDSS, EMAC, and memory access.

Risks: topology errors can be hard to diagnose because this driver contains no active policy beyond data. SDX55 has broad system NoC fan-out from nodes like `qhm_qdss_bam`, `qnm_aggre_noc`, and `qnm_ipa`; missing a target can break apparently unrelated debug or modem data paths. The `bcm_sn7` definition contains repeated `xm_emac` membership, which may be deliberate hardware modeling or a copy/paste-sensitive area to validate. Binding ID mismatches against `qcom,sdx55.h` or DTS consumers will cause wrong node lookup.

Test signals: compile with the SDX55 interconnect driver enabled, check OF modalias generation, and boot an SDX55 board or DT with all three providers registered. Runtime tests should exercise IPA, PCIe, USB3, SDCC, QDSS trace, and memory bandwidth requests while watching RPMh vote/debugfs state. Schema validation should confirm the three compatible strings and consumer phandle IDs.
