# sources/distributed-fs/ceph-client/net/dsa/tag_mxl-gsw1xx.c

Purpose: DSA tag driver for MaxLinear GSW1xx switches using an 8-byte special tag identified by `ETH_P_MXLGSW`.

Important APIs/functions: `gsw1xx_tag_xmit()` inserts the tag after source MAC, sets the MaxLinear ethertype, enables port map and learning disable bits, and writes destination mask. `gsw1xx_tag_rcv()` validates the ethertype, extracts source-port map bits, maps the user port, and strips the special tag. `gsw1xx_netdev_ops` registers `DSA_TAG_PROTO_MXL_GSW1XX`.

Control flow: TX creates headroom with `skb_push()` and `dsa_alloc_etype_header()`. RX checks `pskb_may_pull()`, rejects invalid marker/source port with rate-limited warnings, then removes the header and fixes checksums.

State and persistence: stateless; all route metadata is packet-local.

Dependencies and integration: depends on MaxLinear ethertype constants, Linux bitfield helpers, skb helpers, and the DSA tag framework.

Risks and test signals: risks include wrong RX bitfield interpretation, malformed tag logging floods, and missing offload-forward marking if hardware-forwarded traffic reaches a bridge. Tests should include valid/invalid ethertype, all source ports, port masks, short frames, and bridge duplicate-forwarding checks.
