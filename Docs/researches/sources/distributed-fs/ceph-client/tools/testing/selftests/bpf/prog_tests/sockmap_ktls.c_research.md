<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c

Purpose: `sockmap_ktls.c` tests interactions between sockmap/sockhash and kernel TLS sockets. It validates that sockmap update rejects sockets already using a ULP, that basic kTLS offload data transfer works, and that SK_MSG verdict programs can cork, push, redirect under buffer pressure, and pop bytes on kTLS TX paths.

Important APIs/types/functions: `init_ktls_pairs()` enables TCP ULP `"tls"` on both endpoints and configures TLS 1.2 AES-GCM-128 TX/RX crypto info. `create_ktls_pairs()` creates a connected pair and initializes kTLS. `test_sockmap_ktls_update_fails_when_sock_has_ulp()` checks map update rejection after TCP_ULP is set. `test_sockmap_ktls_offload()`, `test_sockmap_ktls_tx_cork()`, `test_sockmap_ktls_tx_no_buf()`, and `test_sockmap_ktls_tx_pop()` exercise data transfer and SK_MSG policy operations. `test_sockmap_ktls()` dispatches map/family combinations and IPv4/IPv6 stream kTLS tests.

Control flow: map update tests create an explicit sockmap or sockhash, create/connect a TCP socket, set TCP_ULP to TLS, assert `bpf_map_update_elem()` fails, then confirm normal TCP setsockopt still dispatches through saved protocol operations. kTLS data tests create socket pairs, attach SK_MSG verdict programs to a sockmap, insert sockets, initialize TLS, set BSS policy knobs (`cork_byte`, `push_start/end`, `apply_bytes`, `pop_start/end`), send data, and validate received length/content or send-loop behavior under buffer pressure.

State and persistence: state includes transient TCP socket pairs, kTLS socket state and crypto info, BPF sockmaps, attached SK_MSG verdict programs, skeleton BSS policy fields, and send/receive buffers. No durable files are created.

Dependencies: requires kernel TLS (`TCP_ULP` `"tls"`, `SOL_TLS`, `TLS_TX`, `TLS_RX`), TLS 1.2 AES-GCM-128 support, sockmap/sockhash, SK_MSG verdict helpers, IPv4/IPv6 TCP, and generated skeletons `test_skmsg_load_helpers` and `test_sockmap_ktls`.

Integration points: bridges kernel TLS protocol replacement with sockmap map-update rules and SK_MSG data manipulation helpers (`cork`, `push`, `pop`, redirect/apply-bytes behavior) on encrypted socket paths.

Risks: kTLS availability is kernel/config dependent and may require crypto support. The source snapshot contains likely bugs in helper formatting (`fmt_test_name()` uses constants rather than parameters) and duplicated `ASSERT_OK(create_pair())` text in `test_sockmap_ktls_tx_no_buf()`. The offload test checks `ASSERT_OK(err, "send(msg)")` after `send()` without assigning `err`, so content/length assertions are more meaningful than that check. Buffer-pressure send loops rely on nonblocking send eventually failing.

Test signals: map update fails for ULP sockets across IPv4/IPv6 and sockmap/sockhash, simple TLS send/recv preserves data and length, cork delays data until full message, push increases received length with expected skipped bytes, no-buffer path exits cleanly under constrained buffers, and pop policies remove the requested byte ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c -->
