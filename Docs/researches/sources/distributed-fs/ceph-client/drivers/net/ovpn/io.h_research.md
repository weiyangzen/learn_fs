# sources/distributed-fs/ceph-client/drivers/net/ovpn/io.h

Purpose: defines ovpn I/O constants and function prototypes shared by the netdev, crypto, peer, and transport paths.

Important APIs/types/functions: `OVPN_HEAD_ROOM` computes required encapsulation headroom for DATA_V2 AEAD plus UDP/TCP and IPv4/IPv6 headers. `OVPN_MAX_PADDING`, `OVPN_KEEPALIVE_SIZE`, `ovpn_keepalive_message`, `ovpn_net_xmit()`, `ovpn_recv()`, `ovpn_xmit_special()`, `ovpn_encrypt_post()`, and `ovpn_decrypt_post()` form the public I/O interface.

Control flow: no runtime logic in the header; it establishes sizing assumptions used by netdev setup and AEAD skb headroom checks.

State and persistence: no state, except declaration of the keepalive byte sequence defined in `io.c`.

Dependencies and integration: depends on ovpn protocol constants and transport header sizes. Used by `main.c` to set MTU/headroom/tailroom and by `crypto_aead.c` for encryption headroom.

Risks: if OpenVPN header/tag sizes or transport assumptions change, `OVPN_HEAD_ROOM` must stay synchronized or encryption may fail with insufficient headroom. Tailroom and padding constants affect advertised netdev limits.

Test signals: compile-time users, MTU/headroom validation, encryption on skbs near headroom limits, and keepalive-size consistency tests.
