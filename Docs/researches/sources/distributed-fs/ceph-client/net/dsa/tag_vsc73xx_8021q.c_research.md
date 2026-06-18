# sources/distributed-fs/ceph-client/net/dsa/tag_vsc73xx_8021q.c

Purpose: VLAN/tag_8021q-based DSA tagger for Vitesse VSC73XX switches.

Important APIs/functions: `vsc73xx_xmit()` chooses standalone or bridge-domain tag_8021q VID and inserts a VLAN tag. `vsc73xx_rcv()` decodes tag_8021q source information and maps the user device with fallback helpers. `vsc73xx_8021q_netdev_ops` registers `DSA_TAG_PROTO_VSC73XX_8021Q`.

Control flow: normal TX targets the precise standalone VID. Bridge-offloaded TX under VLAN-unaware bridges uses the bridge VID; under VLAN-aware bridges it returns the original skb because the bridge VLAN should carry the classification. RX initializes source fields to unknown, calls `dsa_8021q_rcv()`, finds the user device, warns on failure, and marks hardware-forwarded frames.

State and persistence: no tagger-owned state; it relies on tag_8021q registration by the switch driver.

Dependencies and integration: depends on generic tag_8021q helpers, bridge VLAN state, DSA user mapping, and promiscuous conduit mode.

Risks and test signals: bridge-mode decisions are the main risk. Tests should cover standalone, VLAN-unaware bridge, VLAN-aware bridge, VBID fallback, non-DSA VLAN RX, and unknown source decode.
