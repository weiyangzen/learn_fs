# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tls.c

## Purpose
`tls.c` is a comprehensive kselftest harness for the Linux kernel TLS ULP. It validates TLS socket setup, supported cipher/version combinations, send/receive data paths, zero-copy/sendfile/splice behavior, control records, TLS 1.3 rekeying, error handling, polling/epoll readiness, record sizing, IPv6 socket operations, prequeue behavior, and edge cases around zero-length records and partial records.

## Important APIs, Functions, and Types
The file uses `kselftest_harness.h` fixtures and variants. `struct tls_crypto_info_keys` wraps all tested `linux/tls.h` crypto-info layouts and stores the active length. `tls_crypto_info_init` initializes the right crypto info for AES-GCM, ChaCha20-Poly1305, SM4, AES-CCM, and ARIA variants. `ulp_sock_pair` creates a connected TCP pair and enables `TCP_ULP` `"tls"` on both ends, marking `notls` when the kernel lacks TLS. `tls_send_cmsg`, `__tls_recv_cmsg`, and `tls_recv_cmsg` exercise `SOL_TLS` record type control messages. `memrnd`, `chunked_sendfile`, `test_mutliproc`, `parse_tls_records`, `tls_send_keyupdate`, and `tls_recv_keyupdate` support reusable test patterns.

## Control Flow
Two main fixtures drive most tests: `tls_basic` for setup without keys until individual tests install them, and `tls` with cipher/version variants that install TX on one endpoint and RX on the other. Variant setup skips FIPS-incompatible ciphers when `/proc/sys/crypto/fips_enabled` is set. Tests cover plain ULP pass-through, bad cipher/version rejection, record sequence wrap, sendfile and chunk boundaries, `MSG_MORE`/`MSG_EOR`, sendmsg and recvmsg scatter/gather, splice in both directions, peek semantics, low-water behavior, bidirectional TLS, blocking and nonblocking transfer, multiprocessing stress, control messages, shutdown/reuse, getsockopt validation, bad iov recovery, TLS 1.3 rekey and polling behavior, raw zero-length AES-CCM record sequences, malformed record/authentication errors, timeout behavior, partial-record poll/epoll readiness, TX max payload sizing, non-established ULP rejection, key-size acceptance, no-pad getsockopt/setsockopt, IPv6 operations, prequeued encrypted data, and data-steal race behavior.

## State and Persistence
State is mostly per-test socket state: connected TCP sockets, installed TLS TX/RX keys, record sequence numbers, pending open records, pipe buffers, temporary anonymous files, child processes, and poll/epoll waiters. The constructor reads but does not write `/proc/sys/crypto/fips_enabled`. Some tests create temporary files with `mkstemp` or `O_TMPFILE` and unlink/close them. No repository files are modified.

## Dependencies and Integration Points
Dependencies are Linux kTLS support, `linux/tls.h`, `linux/tcp.h`, TCP sockets, splice/vmsplice/sendfile support, epoll/poll, fork/wait, and the kselftest harness. Integration points include `TCP_ULP`, `SOL_TLS` options `TLS_TX`, `TLS_RX`, `TLS_RX_EXPECT_NO_PAD`, `TLS_TX_MAX_PAYLOAD_LEN`, `TLS_SET_RECORD_TYPE`, `TLS_GET_RECORD_TYPE`, kernel crypto implementations, FIPS mode policy, and TCP/TLS receive queue interactions.

## Risks and Test Signals
Risks include kernel feature skew by cipher, FIPS-mode skips, architecture differences in pipe sizing and nonblocking timing, forked-child failure propagation, and intentionally corrupted TLS records leaving sockets in error states. Strong signals are kselftest assertions over exact return values and `errno`, byte-for-byte plaintext equality, expected skips for unsupported TLS/FIPS cases, proper readiness transitions for poll/epoll, and successful behavior across every fixture variant.
