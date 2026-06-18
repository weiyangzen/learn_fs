# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/rpmsg_wwan_ctrl.c

Purpose: adapts Qualcomm-style RPMSG control channels to WWAN ports for QMI and AT traffic.

Important APIs/functions: `rpmsg_wwan_ctrl_probe()` finds the first platform-device ancestor as the WWAN parent, allocates `struct rpmsg_wwan_dev`, and creates a WWAN port of the type from the RPMSG ID table. `rpmsg_wwan_ctrl_start()` creates a dedicated RPMSG endpoint using the RPMSG device source address and channel name. `rpmsg_wwan_ctrl_callback()` copies inbound RPMSG payloads into SKBs and forwards them with `wwan_port_rx()`. TX is provided by nonblocking `rpmsg_wwan_ctrl_tx()`, blocking `rpmsg_wwan_ctrl_tx_blocking()`, and `rpmsg_wwan_ctrl_tx_poll()`.

Control flow and state: state is minimal: RPMSG device, WWAN port, and endpoint pointer. Endpoint lifetime is tied to WWAN port start/stop. Remove unregisters the WWAN port; devm allocation handles memory.

Dependencies and integration points: depends on RPMSG core, platform-device ancestry for WWAN device grouping, and WWAN port core. Supported RPMSG channel names include `DATA5_CNTL` as QMI and `DATA4`/`DATA1` as AT.

Risks and test signals: endpoint creation failure, parent selection assumptions, TX before start, and callback allocation failure are main risks. Test open/close, poll behavior, blocking/nonblocking TX, inbound RX, and remove with a live port.
