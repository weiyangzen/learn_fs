# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_mmap.c

## Purpose
`tcp_mmap.c` is a reference and performance selftest for TCP receive zero-copy via `TCP_ZEROCOPY_RECEIVE` and socket `mmap()`. It can run as a server or sender, supports optional sender zerocopy, hashing, pacing, buffer sizing, MSS tuning, and SHA-256 integrity verification.

## Important APIs, Types, And Functions
Major functions are `hash_zone()`, `mmap_large_buffer()`, `tcp_info_get_rcv_mss()`, `child_thread()`, `apply_rcvsnd_buf()`, `setup_sockaddr()`, `do_accept()`, `default_huge_page_size()`, `randomize()`, and `main()`. It uses `struct tcp_zerocopy_receive`, `TCP_ZEROCOPY_RECEIVE`, `SO_ZEROCOPY`, `MSG_ZEROCOPY`, `SO_RCVLOWAT`, `TCP_MAXSEG`, `SO_MAX_PACING_RATE`, OpenSSL EVP SHA-256 APIs, and hugepage or populated anonymous mappings.

## Control Flow
In server mode, `main()` listens and `do_accept()` spawns a detached `child_thread()` per connection. The child maps a large receive buffer, optionally maps the socket for zero-copy receive, polls, calls `getsockopt(TCP_ZEROCOPY_RECEIVE)`, accounts mmaped bytes, reads skip-hint bytes normally, hashes or digests data if requested, and reports throughput and CPU usage. In client mode, `main()` connects, optionally enables sender zerocopy and integrity hashing, then sends a 32 GiB stream from a large buffer, appending a SHA-256 digest when integrity mode is enabled.

## State, Persistence, And Dependencies
State is command-line configuration, heap/mmap buffers, socket mappings, per-thread throughput counters, optional digest state, and socket buffer settings. It depends on Linux TCP zero-copy receive support, OpenSSL, IPv4/IPv6 networking, and sufficient memory or fallback mapping capacity. No persistent files are written.

## Integration Points
This program is both documentation and a stress tool for the TCP mmap receive API. It integrates VM mapping behavior, TCP receive queues, socket options, sender pacing, and optional integrity verification.

## Risks
The default transfer size is very large, so runtime and resource usage are significant. Hugepage mapping may fail and falls back with a warning. `keepflag` is parsed but not functionally used in the visible code. The server loops forever. Integrity mode depends on OpenSSL availability and sends a digest after exactly `FILE_SZ` bytes.

## Test Signals
Useful signals are high mmap percentage when `-z` is enabled, correct SHA-256 when `-i` is enabled, no read or getsockopt errors, and throughput/cpu output showing successful receipt. Failures include mapping failures, connect/listen errors, digest mismatch, or unexpectedly low zero-copy coverage.
