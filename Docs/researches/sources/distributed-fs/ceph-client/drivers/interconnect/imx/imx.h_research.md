# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.h

Purpose: shared i.MX interconnect type, register, and topology macro contract.

Important APIs/types/functions: defines NoC mode/priority constants, register offsets, `struct imx_icc_provider`, `struct imx_icc_node_adj_desc`, `struct imx_icc_node_desc`, `struct imx_icc_noc_setting`, topology macros, and lifecycle prototypes.

Control flow: SoC files use macros to build node/link descriptors; `imx.c` consumes those descriptors during probe.

State and persistence: no runtime state, but structure layouts define provider and node metadata used by all i.MX drivers.

Dependencies/integration: Linux args/bits/types and interconnect provider APIs.

Risks and test signals: test macro link counts against `IMX_ICC_MAX_LINKS`, sparse ID handling, and register constants against hardware documentation.
