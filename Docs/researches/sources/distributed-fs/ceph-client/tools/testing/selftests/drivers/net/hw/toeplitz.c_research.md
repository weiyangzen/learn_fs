
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.c`

## Purpose
Implements the packet receiver/verifier used by `toeplitz.py`. It validates NIC-provided RX hash values against a userspace Toeplitz calculation and can also validate RSS queue-to-CPU or RPS CPU selection.

## Important APIs, Types, And Functions
- `toeplitz()` computes the Toeplitz hash over IPv4/IPv6 4-tuples using the configured RSS key.
- `verify_rxhash()`, `verify_rss()`, and `verify_rps()` compare kernel packet metadata against software expectations.
- `setup_ring()`, `create_ring()`, `setup_rings()`, `recv_block()`, and `process_rings()` use PF_PACKET, TPACKET_V3, `PACKET_FANOUT_CPU`, and `TP_FT_REQ_FILL_RXHASH`.
- `read_rss_dev_info_ynl()` fetches RSS key and indirection table through ethtool YNL generated bindings.
- `parse_opts()` handles IPv4/IPv6, TCP/UDP, destination port, interface, explicit key, RSS CPU list, RPS bitmap, timeout, sink, and verbose mode.

## Control Flow
`main()` parses options, optionally opens a sink socket, creates one packet ring per CPU in a CPU fanout group, signals ksft readiness, processes rings until enough hash-bearing packets arrive or timeout, cleans up rings, and returns the number of frame verification errors.

## State And Persistence
Global process state stores config options, RSS key/table, RX queue CPU mapping, RPS silo mapping, packet rings, and frame counters. It maps packet rings with `MAP_LOCKED | MAP_POPULATE` and releases them during cleanup.

## Dependencies And Integration Points
Depends on Linux PF_PACKET v3, classic BPF socket filters, PACKET fanout, ethtool YNL generated userspace headers (`ynl.h`, `ethtool-user.h`), kselftest readiness helpers, and the NIC providing `tp_rxhash` metadata.

## Risks
The receiver supports up to 65536 CPU rings for RSS mode and exits if CPU count exceeds `RSS_MAX_CPUS`; memory use can be high on large systems. It assumes RSS key length 40 to 256 bytes and a 4-tuple hash. RPS mode is limited to 16 CPUs.

## Test Signals
The program prints counts for pass/nohash/fail, errors out on too few verifiable frames, and exits nonzero if any computed hash, RSS CPU, or RPS CPU mismatch is found.
