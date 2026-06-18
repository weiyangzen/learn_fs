# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/kaanapali.c

Purpose: SoC topology driver for Qualcomm Kaanapali RPMh NoC fabrics. It declares the interconnect nodes, BCM groups, fabric descriptors, regmap ranges, OF compatible table, and platform-driver glue required for the shared RPMh interconnect backend.

Important APIs/types/functions: the file is primarily static data: many `struct qcom_icc_node` objects for CNOC, GEM_NOC, LPASS, memory, multimedia, NSP, PCIe, and system NoC endpoints; `struct qcom_icc_bcm` objects such as `bcm_acv`, `bcm_ce0`, `bcm_cn0`, `bcm_mc0`, `bcm_mm0/mm1`, `bcm_qup*`, `bcm_sh*`, `bcm_sn*`, and `bcm_co0`; descriptor arrays for `kaanapali_aggre_noc`, `clk_virt`, `cnoc_cfg`, `cnoc_main`, `gem_noc`, LPASS fabrics, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`; and `qnoc_driver` using `qcom_icc_rpmh_probe()`/`qcom_icc_rpmh_remove()`.

Control flow: module initialization registers the platform driver at `core_initcall`. OF compatible matching selects the right `qcom_icc_desc`, after which the shared RPMh probe creates ICC nodes, links the graph, initializes BCMs, optionally maps regmaps, programs QoS data, and registers the provider. Runtime bandwidth changes are handled entirely by the shared RPMh ICC callbacks and BCM voter.

State and persistence: static qnode and BCM objects persist for the module lifetime. Per-provider runtime state lives in `icc-rpmh.c`; this file contributes immutable topology, bus widths, channel counts, link relationships, BCM membership, vote scaling/keepalive flags, and QoS register offsets.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,kaanapali-rpmh.h` for binding IDs, the RPMh shared header, BCM voter, ICC core, OF platform, regmap, and module infrastructure. Compatible strings cover Kaanapali aggre, clock virtual, CNOC, GEM, LPASS, memory, multimedia, NSP, PCIe, and system fabrics.

Risks and test signals: most failures would be topology mismatches rather than algorithmic bugs. `aggre_noc` and `pcie_anoc` set `qos_requires_clocks`, so missing clocks prevent QoS programming. Validate every compatible probes, node indexes match the binding header, links resolve to initialized nodes, BCM command-DB names exist, QoS port offsets fit the regmap max register, child providers synchronize through `icc_sync_state`, and module unload unregisters after `core_initcall` registration.
