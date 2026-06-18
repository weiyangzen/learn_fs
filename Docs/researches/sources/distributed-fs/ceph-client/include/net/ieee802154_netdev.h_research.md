# sources/distributed-fs/ceph-client/include/net/ieee802154_netdev.h

Purpose: declares IEEE 802.15.4 netdevice MAC header formats, address conversion helpers, skb control metadata, MAC parameters, link-layer security callbacks, and MLME operations.

Important APIs/types: header structs model beacon, MAC command, security, frame-control, association, disassociation, and composite frame types. Enums cover frame version, addressing mode, association status, and disassociation reason. APIs push/pull/peek headers and MAC command payloads, compute max payload/header length, and compare/convert addresses. `struct ieee802154_mac_cb` overlays skb control data. `ieee802154_mac_params` stores PAN/channel/CSMA and timing parameters. `ieee802154_llsec_ops` and `ieee802154_mlme_ops` define security and management operations.

Control flow and state: transmit callers build an `ieee802154_hdr`, push it into an skb, and pass to device code. Receive callers pull or peek headers, initialize `mac_cb`, and dispatch MLME/security operations. Persistent state lives in netdevice/private WPAN PHY, MAC parameters, and security tables, not this header.

Dependencies and integration: depends on AF IEEE802154, netdevice, skbuff, Linux IEEE802154 types, and cfg802154. It integrates with low-rate wireless drivers and 6LoWPAN stacks.

Risks: variable address modes and security headers make length calculation error-prone. skb control-block size must hold `ieee802154_mac_cb`. Tests should cover all addressing modes, short/extended address conversion, beacon/MAC command push-pull round trips, security callbacks, MLME operations, scan types, and malformed/truncated frames.
