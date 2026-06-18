# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_modem.c

Purpose: implements the modem-facing RMNet raw-IP network device and modem subsystem restart handling for IPA.

Important APIs/functions: `ipa_modem_start()` allocates/registers `rmnet_ipa%d`, binds AP modem TX/RX endpoints to the netdev, and transitions modem state to running. `ipa_modem_stop()` unregisters the netdev and clears endpoint backpointers. `ipa_open()`/`ipa_stop()` enable and disable modem endpoints under runtime PM. `ipa_start_xmit()` validates QMAP SKBs, coordinates runtime PM and netdev queue stop/wake, and calls `ipa_endpoint_skb_tx()`. `ipa_modem_skb_rx()` injects received SKBs into the network stack. `ipa_modem_config()` registers a Qualcomm SSR notifier.

Control flow: netdev open powers IPA, enables TX then RX endpoints, and starts the queue. TX always stops the queue before runtime PM get to avoid racey wake/stop ordering; if power is inactive it returns `NETDEV_TX_BUSY` and resume work later wakes the queue. RX completion from endpoint code calls `ipa_modem_skb_rx()`. SSR before shutdown invokes crash cleanup: disable setup-ready IRQ, pause modem endpoints, clear HOL blocking, reset route tables, flush hash caches, reset modem exception endpoints, unpause, stop netdev, and zero modem memory.

State/persistence: `atomic_t ipa->modem_state` serializes start/stop transitions. `ipa->modem_netdev`, endpoint `netdev` pointers, and per-netdev `struct ipa_priv` persist while the modem netdev is registered. The SSR notifier persists until deconfig.

Dependencies/integration: depends on netdevice/RMNet/QMAP APIs, runtime PM, endpoint TX/RX lifecycle, table reset/flush, memory zeroing, SMP2P reset notification, microcontroller power, and qcom remoteproc SSR notifiers.

Risks: modem start/stop races are controlled by atomics but failed remove may intentionally leak if modem stop cannot complete. TX drops zero-length, wrong-protocol, or too-fragmented packets. Crash recovery ordering is critical to prevent modem endpoints from sending into stale route/status state.

Test signals: `rmnet_ipa` appears after QMI readiness, open/close enables endpoints, QMAP traffic updates stats, runtime resume wakes TX queue, and SSR cycles stop/restart modem traffic without endpoint or memory errors.
