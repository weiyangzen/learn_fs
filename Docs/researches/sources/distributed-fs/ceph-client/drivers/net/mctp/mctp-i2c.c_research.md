<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c

Purpose: implements the DMTF MCTP SMBus/I2C transport binding as ARPHRD_MCTP netdevices. It creates one netdev per eligible I2C adapter and, for mux trees, shares one slave `i2c_client` on the root adapter across child bus netdevices selected by the `mctp-controller` property.

Important APIs/types/functions: `struct mctp_i2c_client` owns the hardware slave client, local link address, selected receive device, and child device list. `struct mctp_i2c_dev` owns the netdev, adapter reference, RX buffer/completion, TX kthread, skb queue, bus lock counters, and `allow_rx`. Key functions are `mctp_i2c_new_client`, `mctp_i2c_slave_cb`, `mctp_i2c_recv`, `mctp_i2c_header_create`, `mctp_i2c_xmit`, `mctp_i2c_tx_thread`, `mctp_i2c_release_flow`, `mctp_i2c_add_netdev`, adapter notifiers, and module init/exit.

Control flow: probe registers an I2C slave callback, then scans existing adapters. Adapter add/delete notifications create or remove netdevs. RX accumulates bytes from I2C slave events, validates command, length and PEC, strips the I2C header, fills `mctp_skb_cb` with the source slave address, and calls `netif_rx`. TX builds an SMBus packet header via `header_ops`, queues skb work, computes PEC, sends with `__i2c_transfer`, and updates stats.

State and persistence: runtime-only state is held in kernel objects, lists, refcounts, skb queues, kthreads, completions, and I2C bus locks. MCTP flow extensions drive `dev_flow_state`; active flows keep the I2C segment locked until `release_flow` queues an unlock marker. No persistent storage exists.

Dependencies/integration: depends on I2C slave support, optional I2C mux root discovery, OF `mctp-i2c-controller` / `mctp-controller`, netdev/MCTP core registration via `mctp_register_netdev`, and SMBus PEC helpers. It integrates tightly with MCTP flow lifecycle to preserve request/response bus ownership.

Risks and test signals: main risks are lock/refcount imbalance, RX racing unregister, malformed byte counts or PECs, mux selection mistakes, and TX queue backpressure. Useful tests include I2C mux add/remove, flow release under error, malformed frame rejection, netdev unregister while RX is in progress, and hardware or emulated PEC interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c -->
