<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c

Purpose: Implements a virtio-net vDPA simulator frontend that loops accepted TX packets back to RX, handles basic control VQ MAC changes, and exports vendor queue stats.

Important APIs/functions: `vdpasim_net_dev_add()` creates and registers the net simulator. `vdpasim_net_work()` processes TX/RX/CVQ traffic. `vdpasim_handle_cvq()` handles control VQ descriptors; `vdpasim_handle_ctrl_mac()` supports `VIRTIO_NET_CTRL_MAC_ADDR_SET`. `vdpasim_net_get_stats()` emits RX/TX/CVQ stats via netlink attributes. `vdpasim_net_set_attr()` updates MAC after device creation.

Control flow: Module init registers a management device supporting MAC, MTU, and feature config attrs. `dev_add` creates the simulator, initializes net config from requested attrs or default MTU 1500, initializes stats, allocates a page buffer, and registers the device. Work first handles CVQ, then loops TX descriptors: pull packet into buffer, filter by broadcast/multicast/current MAC, get RX descriptor, push packet, complete TX and RX, notify, and reschedule after a small batch.

State and persistence: `struct vdpasim_net` embeds common simulator state plus TX/RX/CVQ stats and a page buffer. MAC and MTU live in the simulator config buffer. Stats persist for the device lifetime only.

Dependencies and integration points: Uses virtio-net UAPI, ethernet helpers, netlink attributes for vendor stats, u64 stats synchronization, vringh IOTLB, and simulator core.

Risks: Data path is intentionally simple loopback and filters only destination MAC/broadcast/multicast. Control VQ only supports MAC address set. Stats include `tx_drops` output but code never increments it. Packet buffer is limited to one page per processed descriptor.

Test signals: Add device with MAC/MTU/features, run packet loopback for unicast/broadcast/multicast and filtered destinations, change MAC via CVQ and netlink attr set, query vendor stats for queues 0/1/2, test invalid queue index, and verify behavior when RX queue lacks descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c -->
