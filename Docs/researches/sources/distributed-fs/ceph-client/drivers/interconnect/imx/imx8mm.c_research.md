# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mm.c

Purpose: i.MX8MM topology driver for NOC, DRAM/OCRAM, A53, VPU, GPU, display/MIPI, HSIO, audio, Ethernet, SDMA, NAND, and USDHC paths.

Important APIs/types/functions: `imx8mm_dram_adj` and `imx8mm_noc_adj` use divisor 16. `nodes[]` describes binding IDs, names, and links. `imx8mm_icc_probe()` calls `imx_icc_register()` without NoC register settings.

Control flow: platform-driver probe delegates to the common helper; remove delegates to `imx_icc_unregister()`. Runtime votes use shared standard aggregation and PM QoS for adjustable NOC/DRAM nodes.

State and persistence: static topology descriptors; runtime provider/node/QoS state is owned by `imx.c`.

Dependencies/integration: `dt-bindings/interconnect/imx8mm.h`, platform driver glue, common i.MX helper.

Risks and test signals: validate every master path to DRAM/OCRAM, binding ID indexing, DDRC phandle behavior, and simplified PL301 modeling under multimedia/storage/network workloads.
