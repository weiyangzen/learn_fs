# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx75.c

Purpose: defines Qualcomm SDX75 interconnect providers for a newer RPMh modem platform. It models six providers: clock virtual, DC NoC, GEM NoC, memory-controller virtual, PCIe aggregation NoC, and system NoC. Compared with SDX55/SDX65, the topology adds GEM NoC, multiple PCIe controllers, Ethernet blocks, MVMSS, and a QUP core clock path.

Important APIs/types/functions: uses about 85 `qcom_icc_node` objects, 10 `qcom_icc_bcm` groups, and six `qcom_icc_desc` descriptors. It includes `icc-common.h` in addition to `bcm-voter.h` and `icc-rpmh.h`, reflecting shared descriptor/node helpers. Important BCMs include `CN0` for a large keepalive config/system group, `MC0`, `QUP0`, `SH0`, `SH1`, and `SN*` groups for system, GEM, PCIe, and memory paths. The driver registers as `qnoc-sdx75` using `qcom_icc_rpmh_probe`, `qcom_icc_rpmh_remove`, and `icc_sync_state`.

Control flow: during core init, `qnoc_driver_init` registers the platform driver via `core_initcall`, making these providers available early. OF matching selects descriptors for `qcom,sdx75-clk-virt`, `qcom,sdx75-dc-noc`, `qcom,sdx75-gem-noc`, `qcom,sdx75-mc-virt`, `qcom,sdx75-pcie-anoc`, and `qcom,sdx75-system-noc`. The common RPMh probe registers nodes and BCM voters. Consumer bandwidth requests later flow through this static graph to RPMh BCM votes.

State and persistence behavior: the file has no local mutable state. The static descriptors are retained for the module lifetime. Keepalive BCMs preserve critical config, memory, and QUP-clock paths. Runtime vote state is external to this file in the interconnect provider and RPMh layers.

Dependencies and integration points: depends on `dt-bindings/interconnect/qcom,sdx75.h`, platform bus OF matching, RPMh BCM voter support, and interconnect consumers for PCIe, Ethernet, IPA, USB, QDSS, SDCC, QUP, GEM/memory, and modem/multimedia subsystems. `core_initcall` is an integration choice: this driver must be ready before later consumers need interconnect paths.

Risks: the large `CN0` keepalive group and multi-PCIe topology are high-risk data areas because incorrect membership can produce either excess always-on votes or missing config access. Descriptor coverage must match DTS provider nodes exactly; a missing provider breaks all consumers for that NoC. Since the DC NoC descriptor has nodes but no BCM list, its behavior relies on common code handling descriptors without BCMs. Multiple PCIe endpoint nodes (`xs_pcie_0/1/2`) and PCIe config paths create room for swapped IDs.

Test signals: build with SDX75 enabled and boot with all six compatible providers. Confirm early registration order does not race consumers, and inspect interconnect debugfs for PCIe/GEM/system paths. Exercise PCIe0/1/2, Ethernet, IPA, USB3, SDCC, QDSS, and QUP activity while checking RPMh votes and absence of probe deferrals.
