# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264-bwmgr.h

Purpose: This header assigns Tegra264 BPMP bandwidth-manager client IDs used by the Tegra264 MC interconnect implementation. The IDs bridge Linux memory-client descriptors to BPMP firmware's BWMGR interface.

Important APIs/types/functions: The file exports only preprocessor constants. IDs cover primary/debug clients, CPU clusters, display, VI, APE, VIFAL, GPU, EQOS, PCIe ports, SDMMC, NVDEC/NVENC/NVJPG, OFAA, XUSB, TSEC, VIC, APEDMA, SE, ISP, HDA, RCE, PVA, and NVPMODEL.

Control flow: There is no executable logic. `tegra264.c` stores these constants in each `struct tegra_mc_client.bpmp_id`; ICC bandwidth requests later pass them to BPMP in `MRQ_BWMGR_INT` messages.

State and persistence: No runtime state is stored. The numeric contract must remain stable with BPMP firmware and device-tree binding expectations.

Dependencies and integration: The header is included by `tegra264.c` and indirectly integrates with Linux ICC, Tegra BPMP firmware, and the Tegra MC client table. It is independent of generic kernel headers.

Risks and test signals: A wrong ID sends a bandwidth vote to the wrong firmware client, causing over-throttling or under-provisioning of an unrelated engine. Test signals include BPMP accepting all ICC requests, expected EMC frequency response under GPU/display/storage/network load, and no bandwidth-related underruns or timeouts.
