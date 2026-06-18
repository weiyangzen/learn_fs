# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_phonet.c

## Purpose
`f_phonet.c` implements a USB CDC Phonet gadget function. It exposes a Linux Phonet network device backed by a USB CDC control/data interface pair, translating between USB bulk transfers and `ETH_P_PHONET` socket buffers. The function is specialized for Nokia/Phonet-style point-to-point networking rather than Ethernet framing.

## Important APIs, types, and functions
`struct f_phonet` embeds `struct usb_function`, holds IN/OUT bulk endpoints, one reusable transmit request, an array of receive requests sized by `phonet_rxq_size`, and a receive-fragment accumulator. `struct phonet_port` is the netdev private area and contains a backpointer to the active USB function guarded by a spinlock. `pn_net_setup()` configures the netdev as `ARPHRD_PHONET`, point-to-point, no-ARP, one-byte hardware address with media value `PN_MEDIA_USB`, Phonet MTU limits, and `phonet_header_ops`.

The netdev entry points are `pn_net_open()`, `pn_net_close()`, and `pn_net_xmit()`. TX validates `skb->protocol == ETH_P_PHONET`, queues the skb data on the USB IN request, stops the net queue, and resumes it in `pn_tx_complete()`. RX is driven by `pn_rx_submit()` and `pn_rx_complete()`, which allocate page-sized USB buffers, assemble multi-fragment Phonet frames into an skb, and deliver complete frames through `netif_rx()`. `pn_set_alt()`, `pn_get_alt()`, and `pn_disconnect()` handle USB activation and reset.

## Control flow
`phonet_alloc_inst()` allocates the configfs instance and default netdev via `gphonet_setup_default()`. `phonet_alloc()` creates a function object with flexible storage for RX requests. `pn_bind()` registers the netdev once, reserves control and data interfaces, autoconfigures bulk endpoints, assigns descriptors, allocates the RX request array and TX request, and leaves the carrier off. When the host selects data altsetting 1, `pn_set_alt()` configures and enables endpoints, installs endpoint driver data, sets `port->usb`, raises carrier, and queues the RX request pool. TX packets can then flow from the Phonet netdev to USB IN. OUT completions resubmit receive requests until disconnect or endpoint reset statuses stop resubmission.

## State and persistence
State persists only in kernel memory: the registered netdev, active `port->usb` pointer, carrier state, endpoint enablement, pending RX pages, in-flight TX skb, and current fragmented RX skb. `phonet_opts->bound` records whether the netdev was registered so instance teardown chooses `gphonet_cleanup()` versus `free_netdev()`. No file or firmware state is stored.

## Dependencies and integration points
The driver integrates with the network stack (`struct net_device`, `netif_rx`, stats, carrier state), the Phonet stack (`linux/if_phonet.h`, `phonet_header_ops`), the USB composite framework, and CDC descriptors. It shares some helper naming with `u_ether` for netdev ifname exposure but uses Phonet-specific framing. Configfs exposes a read-only `ifname` attribute.

## Risks and edge cases
`MAXPACKET` must divide `PAGE_SIZE`, enforced at compile time, because RX pages are accumulated as USB fragments. RX can drop frames if `MAX_SKB_FRAGS` is exceeded or if skb allocation fails. TX uses a single request and a one-entry netdev queue, so throughput is intentionally constrained. The code assumes bind ordering avoids races around `phonet_opts->bound`. Locking is split between the netdev private spinlock and `fp->rx.lock`; reset paths must clear `fp->rx.skb` and disable endpoints while TX/RX callbacks may still complete. Host altsetting 0 leaves the netdev registered but carrier-off.

## Test signals
Tests should create the Phonet function, confirm the `upnlink%d` interface and read-only `ifname`, inspect descriptors for the CDC Phonet control/data interfaces and altsetting 1 data endpoints, bring the netdev up/down, transmit non-Phonet and Phonet skbs to validate drop and queue behavior, stress fragmented OUT transfers including short final packets, and verify disconnect/reset stops resubmission and clears carrier.
