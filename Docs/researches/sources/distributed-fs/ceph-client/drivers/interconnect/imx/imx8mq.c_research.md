# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mq.c

Purpose: i.MX8MQ topology driver for NOC, memory, A53, VPU, GPU, DCSS, USB, display/CSI/LCDIF, audio, Ethernet, SDMA, NAND, USDHC, PCIe, and PL301 main paths.

Important APIs/types/functions: DRAM/NOC adjustment descriptors use divisor 4. `nodes[]` contains the graph. The platform driver sets `.sync_state = icc_sync_state`.

Control flow: probe registers topology without NoC settings. Runtime votes use shared i.MX aggregation/PM QoS. Sync-state eventually clears initial bandwidth floors in the core.

State and persistence: static topology plus runtime provider and PM QoS state in the common helper.

Dependencies/integration: `dt-bindings/interconnect/imx8mq.h`, platform device matching, `icc_sync_state`.

Risks and test signals: test sync-state, PCIe and display paths, DDRC phandle ordering, and whether simplified PL301 modeling satisfies bandwidth-sensitive workloads.
