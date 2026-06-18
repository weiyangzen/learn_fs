
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_path.c

Purpose: Builds `struct nf_flow_route` metadata from nftables packet context, conntrack tuples, routes, neighbours, and netdevice forwarding paths so flows can be installed into the software and hardware flowtable paths.

Important APIs and functions: Exported `nft_flow_route()` computes both directions. `nft_default_forward_path()` initializes dst and xmit type. `nft_dev_fill_forward_path()` validates Ethernet devices and neighbour reachability before calling `dev_fill_forward_path()`. `nft_dev_path_info()` converts path-stack entries into ingress device, output device, encapsulation, tunnel, MAC, and GSO metadata. `nft_flow_tunnel_update_route()` resolves tunnel routes.

Control flow: `nft_flow_route()` holds the current skb dst, routes the opposite direction from conntrack tuple data, initializes both route tuples, then tries to refine neighbour xmit paths into direct L2 forwarding where the discovered ingress device is present in the nft flowtable hook list. Bridge, VLAN, PPPoE, DSA, and tunnel path entries are interpreted into route metadata consumed by core/datapath/offload code.

State and persistence: The file populates caller-provided `nf_flow_route`; it does not own long-lived state. It does take dst references that are later transferred and released by flow allocation/free.

Dependencies and integration: Depends on nftables packet info and hook lists, conntrack tuples, `nf_route()`, neighbour state, `dev_fill_forward_path()`, bridge/VLAN/PPPoE path descriptors, and flowtable hardware-offload flags.

Risks: Bad route metadata can send fast-path packets to the wrong device or with wrong encapsulation. Important risks include neighbour validity races, dst reference ownership, direct forwarding only when flowtable hooks cover the discovered ingress device, bridge VLAN pop/push accounting, single-tunnel limitation, and preserving GSO segmentation needs for PPPoE. Test signals include routed, bridged, VLAN-stacked, PPPoE, DSA, tunnel, and xfrm paths with device removal and neighbour invalidation.
