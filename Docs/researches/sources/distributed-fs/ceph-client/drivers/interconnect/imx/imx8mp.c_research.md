# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mp.c

Purpose: i.MX8MP topology plus NoC priority settings for NOC, memory, CPU, supermix/GIC/ML, audio, GPU, HDMI, HSIO, media, video, and PL301 main paths.

Important APIs/types/functions: `imx8mp_noc_adj` uses divisor 16. `noc_setting_nodes[]` maps binding IDs to NoC register offsets, fixed priorities, and external-control flags. `nodes[]` defines topology.

Control flow: probe calls `imx_icc_register()` with settings, causing NoC MMIO mapping. On nonzero peak votes, the common helper writes priority/mode/external-control registers for configured nodes.

State and persistence: hardware priority/mode state persists after writes; provider/QoS state lives in `imx.c`.

Dependencies/integration: `dt-bindings/interconnect/fsl,imx8mp.h`, MMIO mapping, common i.MX helper.

Risks and test signals: test register offsets, peak-zero skip behavior, unsupported modes, media/HDMI priority, sparse binding ID indexing, and MMIO mapping failure.
