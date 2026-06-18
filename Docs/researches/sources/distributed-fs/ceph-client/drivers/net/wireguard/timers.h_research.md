# sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.h

Purpose: Declares WireGuard per-peer timer lifecycle/event hooks and provides a coarse-boottime expiration helper.

Important APIs: Declares timer init/stop plus event notification functions for data sent/received, authenticated packet sent/received/traversal, handshake initiation/completion, and session derivation. `wg_birthdate_has_expired()` compares a nanosecond birthdate plus seconds to coarse boottime.

Control flow: Send, receive, device stop, peer create/remove, and Noise session derivation use these hooks to drive rekey/keepalive behavior.

State and persistence: No header-owned state; declared functions mutate peer timers and related peer fields.

Dependencies and integration points: Includes `linux/ktime.h` and forward-declares `struct wg_peer`.

Risks: Expiration helper casts to signed 64-bit for wrap-safe comparison; callers must pass coarse-boottime-compatible birthdates. Event hooks must be called in the right datapath places or rekey/keepalive behavior changes.

Test signals: Compile coverage and send/receive timer behavior around key age, keepalive, and retry boundaries.
