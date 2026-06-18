# sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rawmode.c

Purpose: ARCNET raw packet encapsulation module. It uses only the hardware ARCNET header and no software protocol header, exposing packets as `ETH_P_ARCNET`.

Important APIs and functions: `rx()` copies a received card buffer into an skb, using ARCNET offset rules for 256-byte versus 512-byte packet layouts. `build_header()` pushes `ARC_HDR_SIZE`, fills source and destination hardware addresses, and handles loopback/noarp by using destination 0. `prepare_tx()` computes buffer offsets, writes the hardware header and raw payload to the card through `lp->hw.copy_to_card()`, and records `lastload_dest`. `rawmode_proto` supplies `.suffix = 'r'`, MTU `XMTU`, receive/build/prepare callbacks, and no continuation or ack callback.

Control flow: module init replaces default protocol-map entries with raw mode, sets broadcast protocol when no better one exists, and makes raw mode the default. ARCNET core later calls the callbacks from `arcnet_header()`, `arcnet_send_packet()`, and `arcnet_rx()`.

State and dependencies: state is global protocol-map registration plus per-device `lastload_dest`; payload state remains in skbs and card buffers. Dependencies are `arcdevice.h`, exported ARCNET protocol maps, core buffer copy hooks, and netif receive. Risks include raw mode interoperability, length/offset edge cases near `MTU`, `MinTU`, and `XMTU`, and default-protocol takeover affecting other loaded protocol modules. Test signals include module load/unload map restoration, small and extended packet receive/transmit, broadcast destination behavior, and oversized packet clamping warnings.
