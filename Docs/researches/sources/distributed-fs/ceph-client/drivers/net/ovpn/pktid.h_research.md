# sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.h

Purpose: Defines OpenVPN packet-ID transmit/receive state, replay-window constants, and nonce construction helpers.

Important APIs, types, and functions: `struct ovpn_pktid_xmit` contains an atomic sequence number. `struct ovpn_pktid_recv` contains the replay bitmap, base/extent, expiry, highest ID/time, floor, max backtrack, and lock. `ovpn_pktid_xmit_next()` atomically allocates the next ID and rejects wrap to zero. `ovpn_pktid_aead_write()` writes the 12-byte AEAD IV as 4-byte packet ID plus 8-byte nonce tail. `PKTID_RECV_EXPIRE`, `REPLAY_WINDOW_ORDER`, `REPLAY_WINDOW_BYTES`, `REPLAY_WINDOW_SIZE`, and `REPLAY_INDEX()` describe replay tracking.

Control flow: TX callers request an ID before encryption and use it to build nonce material. RX callers initialize per-key replay state and call `ovpn_pktid_recv()` after parsing/decrypting packet ID/time material.

State and persistence behavior: Packet-ID state is per key slot and runtime-only. It must reset on key install to avoid nonce reuse or replay-state bleed between key generations.

Dependencies and integration points: It depends on `proto.h` for nonce size constants and kernel bitmap/atomic/spinlock APIs through included headers. Crypto AEAD code depends on the IV layout matching OpenVPN's wire format.

Risks and edge cases: Reusing a TX packet ID with the same nonce tail and key is catastrophic for AEAD, so `-ERANGE` on wrap must trigger key rotation/drop. `ovpn_pktid_aead_write()` assumes destination space is at least `OVPN_NONCE_SIZE`. The replay window size and index mask require power-of-two sizing.

Test signals: Validate nonce byte order, packet-ID wrap behavior, per-key reset, replay-window macros, and AEAD encryption/decryption interoperability with userspace OpenVPN test vectors.
