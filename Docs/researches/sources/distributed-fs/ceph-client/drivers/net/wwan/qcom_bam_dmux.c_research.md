# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/qcom_bam_dmux.c

Purpose: implements Qualcomm BAM-DMUX WWAN raw-IP network devices over DMAengine RX/TX channels and Qualcomm SMEM power-control handshakes.

Important APIs/functions: `bam_dmux_probe()` obtains IRQs and SMEM state handles, initializes runtime PM, requests threaded PC/PC-ACK IRQs, and powers on if the remote side is already active. `bam_dmux_runtime_resume()` votes for power, waits for ACK and remote `pc_state`, verifies RX DMA initialization, and requests TX DMA. `bam_dmux_rx_callback()` validates DMUX headers and dispatches DATA/OPEN/CLOSE commands. OPEN schedules netdev registration; CLOSE detaches a channel. `bam_dmux_netdev_start_xmit()` queues an SKB in a fixed TX ring, prepends `bam_dmux_hdr`, maps for DMA, and either submits immediately or defers until runtime resume completes. `bam_dmux_power_on()` requests RX DMA and posts 32 RX buffers.

Control flow and state: `struct bam_dmux` owns SMEM PC state, completions/waitqueues, RX/TX DMA channels, fixed arrays of 32 DMA SKBs, a TX ring index, deferred TX bitmap, remote channel bitmap, and per-channel netdevs. Remote channel state drives dynamic `wwan%d` device creation.

Dependencies and integration points: depends on platform device probing, OF compatible `qcom,bam-dmux`, DMAengine, runtime PM, SMEM state, netdev core, and raw-IP/QMAP protocol handling.

Risks and test signals: power handshake timeout, deferred TX during resume, DMA mapping cleanup, remote open/close races, and header validation are key risks. Test runtime suspend/resume under traffic, channel churn, malformed headers, full TX ring, remove while remote PC is asserted, and QMAP/non-IP packet delivery.
