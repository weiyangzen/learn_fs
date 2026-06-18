# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/eliza.c

Purpose: RPMh topology driver for Qualcomm Eliza NoC fabrics, including aggre NoCs, CNOC, GEM_NOC, LPASS, MC virtual, MMSS, NSP, PCIe, and system NoC.

Important APIs/types/functions: static `qcom_icc_node`, `qcom_icc_bcm`, node arrays, BCM arrays, and `qcom_icc_desc` descriptors. `qnoc_of_match[]` maps `qcom,eliza-*` compatibles. Driver uses `qcom_icc_rpmh_probe()`/remove.

Control flow: core-init registers the platform driver. Probe delegates descriptor consumption to the RPMh helper, which initializes BCMs, nodes, links, optional QoS register access, and provider registration. Votes later aggregate into BCM voter RPMh commits.

State and persistence: static topology/BCM descriptors and mutable runtime vote arrays in nodes/BCMs while bound.

Dependencies/integration: Eliza dt-bindings, `icc-rpmh.h`, BCM voter, RPMh, command DB, sync-state.

Risks and test signals: test all compatibles, command DB lookup, QoS clock requirements, large fanout links, wake/sleep votes, bus widths/channels, BCM memberships, and NULL holes.
