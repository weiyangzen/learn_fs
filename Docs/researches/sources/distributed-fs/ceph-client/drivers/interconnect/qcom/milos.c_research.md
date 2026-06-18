# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/milos.c

Purpose: SoC topology driver for Qualcomm Milos RPMh interconnect fabrics. It provides static node graph, QoS boxes, BCM mappings, fabric descriptors, OF match data, and platform-driver registration for the shared RPMh interconnect implementation.

Important APIs/types/functions: the data set includes forward-declared and initialized `struct qcom_icc_node` records for QUP, UFS, USB3, QDSS, crypto, IPA, SDCC, CNOC, GEM_NOC, GPU, LPASS, modem, multimedia, compute, PCIe, SNOC, memory, and service nodes. Many masters include `struct qcom_icc_qosbox` entries with per-port offsets and priority settings. Descriptors cover `milos_aggre1_noc`, `aggre2_noc`, `clk_virt`, `cnoc_cfg`, `cnoc_main`, `gem_noc`, `lpass_ag_noc`, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`.

Control flow: `core_initcall(qnoc_driver_init)` registers `qnoc-milos`. Device-tree matching selects the descriptor for one Milos fabric, and `qcom_icc_rpmh_probe()` creates nodes, initializes BCMs, programs QoS through each descriptor's regmap, registers the provider, and populates child devices. The file itself has no runtime callbacks beyond platform-driver registration and unregister.

State and persistence: static topology nodes retain their dynamic `icc_node` pointers after probe. QoS boxes are static, usually one port each, and their values are written during probe if the corresponding descriptor has a config. BCMs hold runtime vote arrays after shared initialization; descriptors without BCM arrays act as graph-only or pass-through providers.

Dependencies/integration: integrates with `dt-bindings/interconnect/qcom,milos-rpmh.h`, `icc-rpmh.h`, `icc-common.h`, `bcm-voter`, ICC core, OF platform, regmap, and Linux module infrastructure. It uses `icc_sync_state` so consumers can be synchronized with provider readiness.

Risks and test signals: Milos has many QoS-equipped nodes, so offset drift versus hardware documentation is a primary risk. Test each compatible string, probe with and without parent regmap, QoS register writes for all qnodes with `qosbox`, BCM command-DB lookup for all BCM names, path votes across multi-hop links, PCIe dual-root paths, multimedia high-frequency and system-frequency paths, and cleanup after partial probe failures.
