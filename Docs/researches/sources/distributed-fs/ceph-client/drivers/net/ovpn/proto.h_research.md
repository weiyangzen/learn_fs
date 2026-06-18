# sources/distributed-fs/ceph-client/drivers/net/ovpn/proto.h

Purpose: Captures OpenVPN data-channel wire constants and inline helpers for opcode, key ID, peer ID, and AEAD nonce formatting.

Important APIs, types, and functions: Constants include `OVPN_NONCE_SIZE`, `OVPN_NONCE_TAIL_SIZE`, `OVPN_NONCE_WIRE_SIZE`, `OVPN_OPCODE_SIZE`, opcode field masks, `OVPN_DATA_V1`, `OVPN_DATA_V2`, and `OVPN_PEER_ID_UNDEF`. Inline helpers are `ovpn_opcode_from_skb()`, `ovpn_peer_id_from_skb()`, `ovpn_key_id_from_skb()`, and `ovpn_opcode_compose()`.

Control flow: UDP/TCP receive paths pull enough bytes, use `ovpn_opcode_from_skb()` to accept kernel-handled `DATA_V2`, reject `DATA_V1`, or forward control packets to userspace. Decrypt paths use key ID extraction. TX paths compose a 32-bit opcode word containing packet type, key ID, and peer ID.

State and persistence behavior: No mutable state. This header defines a stable in-kernel representation of the OpenVPN wire bit layout.

Dependencies and integration points: It depends on bitfield helpers and skbuff access. It is shared by packet I/O, transports, crypto, and packet-ID nonce helpers.

Risks and edge cases: The inline readers assume the caller has already pulled at least four bytes into linear skb data. Misaligned direct `__be32` casts rely on kernel architectures tolerating the access pattern used elsewhere. Field masks must match UAPI/wire protocol; changing them breaks interoperability.

Test signals: Use packet fixtures for DATA_V1, DATA_V2, undefined peer ID, multiple key IDs, and peer-ID boundaries. Verify compose/extract round trips and non-linear skb paths that first call the expected pull helpers.
