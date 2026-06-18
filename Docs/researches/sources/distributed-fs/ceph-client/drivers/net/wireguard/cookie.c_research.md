# sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.c

## Purpose
`cookie.c` implements WireGuard's handshake MAC and cookie mechanism. It validates MAC1, optionally validates MAC2 cookies tied to source address/port, rate-limits unauthenticated handshake traffic, creates encrypted cookie replies, and consumes cookie replies on peers.

## Important APIs, Types, And Functions
Public functions are `wg_cookie_checker_init()`, `wg_cookie_checker_precompute_device_keys()`, `wg_cookie_checker_precompute_peer_keys()`, `wg_cookie_init()`, `wg_cookie_validate_packet()`, `wg_cookie_add_mac_to_packet()`, `wg_cookie_message_create()`, and `wg_cookie_message_consume()`. Internal helpers are `precompute_key()`, `compute_mac1()`, `compute_mac2()`, and `make_cookie()`. Cryptographic dependencies are BLAKE2s and XChaCha20-Poly1305.

## Control Flow
Initialization seeds the checker secret and lock, while key precomputation derives MAC/cookie keys from static public keys and fixed labels. Outbound handshake messages call `wg_cookie_add_mac_to_packet()`: MAC1 is computed and remembered, then MAC2 is filled only if a still-valid cookie is available. Incoming handshake validation recomputes MAC1 against the device key; if cookie checking is required, it derives a cookie from the rotating secret and packet source address/UDP source port, checks MAC2, and finally asks the ratelimiter before returning `VALID_MAC_WITH_COOKIE`. Cookie replies are created by deriving the same source cookie and encrypting it with the peer's MAC1 as associated data. Cookie replies are consumed by looking up the receiver index, verifying a MAC1 was sent, decrypting, and storing a fresh valid cookie in the peer.

## State And Persistence
`cookie_checker` holds a rotating random secret, birthdate, precomputed device keys, and device pointer. `cookie` holds per-peer decrypted cookie, birthdate, validity flag, last MAC1 sent, sent-MAC flag, precomputed peer keys, and rwsem. Secrets are in memory only and rotate based on `COOKIE_SECRET_MAX_AGE`.

## Dependencies And Integration Points
The module integrates with WireGuard device, peer, index hashtable, timers/birthdate helpers, ratelimiter, skb IP/IPv6/UDP headers, Noise constants, message layouts, BLAKE2s, XChaCha20-Poly1305, and crypto constant-time comparison.

## Risks
Correctness depends on message length including trailing `struct message_macs`; callers must pass complete handshake messages. `make_cookie()` assumes the skb has IP/IPv6 and UDP headers available. Lock ordering around peer cookie rwsem and index lookup must remain consistent with other WireGuard paths. Device key precompute requires the static identity lock as documented by the comment.

## Test Signals
Test MAC1 rejection, valid MAC without cookie, valid MAC2 with ratelimiter allow/deny, cookie secret rotation, encrypted cookie reply creation/consumption, stale cookie latency cutoff, invalid receiver index, consume without prior MAC1, IPv4 and IPv6 source-cookie derivation, and constant-time comparison paths.
