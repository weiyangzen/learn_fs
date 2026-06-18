# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/glymur.c

Purpose: RPMh topology driver for Qualcomm Glymur and Mahua fabrics, covering aggre NoCs, CNOC, HSCNOC, LPASS, MC virtual, MMSS, NSINOC, NSP, OOBM, PCIe east/west, and system NoC.

Important APIs/types/functions: static `qcom_icc_node`/`qcom_icc_bcm` descriptors, many `regmap_config`-backed `qcom_icc_desc` objects, and `glymur_qnoc_probe()` for Mahua-compatible topology patches.

Control flow: probe mutates shared static topology for Mahua variants, then calls `qcom_icc_rpmh_probe()`. Runtime votes aggregate per RPMh bucket and commit through BCM voter.

State and persistence: topology descriptors are static and some are mutated in-place by Mahua compatibility handling; node/BCM aggregate arrays persist while providers are bound.

Dependencies/integration: Glymur dt-bindings, `linux/property.h`, RPMh helper, BCM voter, command DB, sync-state.

Risks and test signals: test every Glymur/Mahua compatible, reprobe after static mutations, PCIe 3A/WLAN NULLing, channel/buswidth changes, regmap ranges, QoS clocks, BCM membership, and keepalive/enable-mask votes.
