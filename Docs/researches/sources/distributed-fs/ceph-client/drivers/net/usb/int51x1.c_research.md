# sources/distributed-fs/ceph-client/drivers/net/usb/int51x1.c

Purpose: Implements a compact usbnet minidriver for Intellon INT51x1 USB powerline adapters, adding the device's two-byte length framing around Ethernet packets.

Important APIs and types: The driver has no private state beyond usbnet. Key functions are `int51x1_bind()`, `int51x1_rx_fixup()`, and `int51x1_tx_fixup()`. `int51x1_netdev_ops` delegates normal netdev operations to usbnet helpers, and `int51x1_info` provides fixed endpoint numbers, `FLAG_ETHER`, the RX/TX fixups, and `usbnet_cdc_update_filter()` for receive filter updates.

Control flow: Probe is handled by `usbnet_probe()`. Bind reads the Ethernet address from string/index 3 via `usbnet_get_ethernet_addr()`, adds the private two-byte header to `hard_header_len`, recomputes `hard_mtu`, swaps in the driver's netdev ops, and asks usbnet to discover endpoints. RX fixup verifies at least a two-byte header is present, reads a little-endian length from the trailing two bytes of the received skb, trims the skb to that length, and lets usbnet continue. TX fixup ensures room for a two-byte little-endian length prefix plus any tail padding needed to avoid short packet/ZLP ambiguity, expands or compacts the skb if needed, pushes the header, stores the masked packet length, appends zero padding, and returns the adjusted skb to usbnet.

State and persistence behavior: There is no persistent device state. Packet framing state is entirely per skb. Statistics, queueing, suspend/resume, disconnect, and endpoint URB handling are owned by usbnet.

Dependencies and integration points: Integrates with usbnet, MII/ethtool headers through usbnet conventions, Ethernet address helpers, CDC receive filter helper, and one USB device ID pair (`0x09e1:0x5121`). It sets endpoint numbers `.in = 1` and `.out = 2` rather than scanning descriptors in the driver itself.

Risks and test signals: RX trusts the device-provided trailing length after only ensuring a minimum frame size; tests should include malformed lengths larger than skb length, tiny frames, and padded frames. TX risk is in headroom/tailroom reshaping and the exact padding rules around `dev->maxpacket`, especially packets shorter than 64 bytes or exact multiples of maxpacket. Build and runtime coverage should exercise MTU changes, multicast filter updates, MAC address setting, suspend/resume through usbnet, and SKB cloned/non-cloned TX paths.
