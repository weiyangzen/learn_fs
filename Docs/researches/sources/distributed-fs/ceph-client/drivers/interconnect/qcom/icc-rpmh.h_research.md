# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.h

Purpose: shared data-model and API header for Qualcomm RPMh interconnect providers. It defines provider, node, BCM, QoS, fabric, and descriptor structures used by RPMh NoC topology files and declares the common probe, remove, aggregation, set, and BCM initialization functions implemented in `icc-rpmh.c`.

Important APIs/types/functions: `to_qcom_provider()` converts an ICC provider to `struct qcom_icc_provider`. `struct qcom_icc_provider` stores the generic provider, device, BCM array, BCM voter, node array, optional QoS regmap, and QoS clocks. `struct bcm_db` mirrors command-DB auxiliary BCM data. `struct qcom_icc_qosbox` describes static QoS register programming. `struct qcom_icc_node` stores name, dynamic `icc_node`, bandwidth buckets, BCM backpointers, bus geometry, QoS pointer, and flexible link-node array. `struct qcom_icc_bcm` stores RPMh vote state and command-DB metadata. `struct qcom_icc_desc` is the per-compatible descriptor consumed by probe.

Control flow: SoC files instantiate static qnodes and BCMs with this schema, arrange them in descriptor arrays, and bind descriptors to OF compatible strings. `qcom_icc_rpmh_probe()` then uses these fields to create ICC nodes, link graph edges, initialize BCMs, configure QoS, and register providers. Runtime ICC callbacks mutate only the bucket arrays and BCM vote state declared here.

State and persistence: the structures are mostly static topology plus per-probe runtime pointers and counters. `MAX_BCM_PER_NODE` bounds how many BCMs can be attached by `qcom_icc_bcm_init()`. `MAX_PORTS`, `MAX_LINKS`, `MAX_BCMS`, and `MAX_VCD` document sizing assumptions used by the implementation and topology tables.

Dependencies/integration: includes Qualcomm interconnect DT bindings and regmap declarations, while relying on types from ICC core, device, clock, list, and BCM voter headers included by users. It is the contract between chip-specific RPMh files and the shared RPMh backend.

Risks and test signals: topology files must keep `num_links`, flexible `link_nodes`, BCM `num_nodes`, and descriptor array indexes consistent with binding IDs. Overflow of `bcms[MAX_BCM_PER_NODE]` is not guarded in the initializer. Compile all RPMh topology files after signature changes, and test malformed or high-fanout topology additions with static analysis or targeted assertions.
