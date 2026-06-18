# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.c

Purpose: Raw-packet generator and receiver for IPv4 and IPv6 fragment reassembly testing, including reordered fragments, duplicate fragments, run patterns, and overlap rejection behavior.

Important APIs and types: Uses raw `IPPROTO_RAW` sockets, UDP sockets, IPv4/IPv6/fragment/UDP headers, custom IPv4 and IPv6 UDP checksum generation, `SO_RCVTIMEO`, `sendto`, `recv`, randomized payload sizes, and options `-4`, `-6`, `-o`, `-p`, `-v`.

Control flow: `main` seeds randomness and runs IPv4 and/or IPv6. `run_test` opens raw transmit and UDP receive sockets, fills a known payload, iterates payload sizes, and either tests many fragment lengths for normal reassembly or one randomized overlap case per payload. `send_udp_frags` initializes headers, chooses in-order, IPv4 run, or odd-then-even ordering, optionally injects a hard-coded or random overlapping fragment, and sends fragments through `send_fragment`. `recv_validate_udp` expects correct payload for normal cases and timeout or optional permissive success for overlap cases.

State and persistence: Global buffers hold the UDP payload and current IP frame. Counters and random seed are process-local and printed for reproducibility. No durable state.

Dependencies and integration: The shell harness configures fragment thresholds/timeouts and netfilter paths. Root is required for raw sockets.

Risks: Randomized paths can expose rare failures but also need the printed seed for reproduction. Overlap behavior differs when netfilter drops invalid packets, hence permissive mode.

Test signals: `PASS` on stderr after each address-family run; failures indicate wrong reassembly, unexpected overlap acceptance, checksum issues, or socket errors.
