<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c

Purpose: implements the DMTF MCTP I3C transport binding. It creates one MCTP netdev per I3C bus whose current master has the `mctp-controller` property, and attaches matching I3C devices with DCR class `I3C_DCR_MCTP`.

Important APIs/types/functions: `struct mctp_i3c_bus` owns the netdev, TX thread, one-slot TX state, local provisioned ID, bus pointer, and device list. `struct mctp_i3c_device` stores the I3C device, IBI setup, dynamic address, read/write limits, provisioned ID, and a mutex. Key functions are `mctp_i3c_bus_add`, `mctp_i3c_add_device`, `mctp_i3c_setup`, `mctp_i3c_ibi_handler`, `mctp_i3c_read`, `mctp_i3c_header_create`, `mctp_i3c_xmit`, and the I3C bus notifier.

Control flow: module init registers the I3C bus notifier, scans existing buses, then registers the I3C device driver. A bus add creates a netdev and TX thread. Device probe finds the owning bus, requests/enables IBI, and records endpoint limits. RX is IBI-driven: the handler filters the mandatory data byte when present and performs a private read transfer. TX looks up the destination provisioned ID from an internal header, appends PEC, and sends a private SDR write transfer.

State and persistence: all state is volatile. `busdevs_lock` protects the global bus list and per-bus device lists. Device mutexes serialize IBI RX, TX, and removal. A single pending TX skb is protected by `tx_lock`; the netdev queue is stopped until the TX thread consumes it.

Dependencies/integration: depends on I3C master/device APIs, OF property discovery on the master node, MCTP netdev registration, 48-bit provisioned IDs as link-layer addresses, and SMBus PEC calculation with I3C dynamic address bytes.

Risks and test signals: risks include unsupported IBI controllers, stale device lookup after endpoint removal, one-slot TX backpressure, max write/read length mismatches, and bus notifier ordering. Tests should cover bus add/remove races, IBI payload filtering, PEC rejection, endpoint `mwl` drops, and probe behavior without `mctp-controller`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c -->
