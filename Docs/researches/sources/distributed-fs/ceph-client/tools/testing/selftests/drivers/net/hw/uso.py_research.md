
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/uso.py`

## Purpose
Tests UDP segmentation offload by sending large UDP datagrams with `UDP_SEGMENT` and verifying both remote payload length and local TX packet counter growth.

## Important APIs, Types, And Functions
- `UDP_SEGMENT = 103` is hardcoded because Python lacks the constant.
- `_send_uso()` sets `IPPROTO_UDP/UDP_SEGMENT`, builds a random payload, and sends one large datagram.
- `_get_tx_packets()` reads `ip -s link` TX packet counters.
- `_test_uso()` enables `tx-udp-segmentation`, runs remote `socat`, sends traffic, and checks segment count.
- `test_uso()` is variant-expanded over IPv4/IPv6 and exact/partial final segment sizes.

## Control Flow
Each variant requires IP version and remote `socat`, enables USO if supported, chooses a UDP port, records TX packets, starts a remote UDP listener, sends one segmented datagram, checks received byte count, waits for stats to settle, then verifies TX packet delta is at least the expected segment count.

## State And Persistence
Mutates `tx-udp-segmentation` feature only if it was initially off; a deferred ethtool call restores it to off. It otherwise uses transient sockets and remote `socat`.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, ethtool feature reporting/toggle support, Python UDP socket options, remote `socat`, and accurate TX packet stats.

## Risks
TX packet counter deltas can include unrelated traffic and therefore only assert a lower bound. A device that offloads but reports stats unusually may still pass due to generic packet counters rather than dedicated USO stats.

## Test Signals
Pass requires the remote stdout length to match total payload and TX packet delta to be greater than or equal to computed segment count for both exact and partial datagram sizes.
