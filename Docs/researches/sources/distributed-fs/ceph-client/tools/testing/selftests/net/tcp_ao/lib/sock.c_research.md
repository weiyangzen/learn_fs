# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/sock.c

## Purpose
`sock.c` is the TCP-AO selftest socket utility layer. It creates listen/connect sockets bound to the test veth, prepares TCP-MD5 and TCP-AO socket option structures, reads TCP-AO per-namespace/per-socket/per-key counters, compares expected counter deltas, and provides client/server echo loops used by many TCP-AO behavior tests.

## Important APIs, Types, And Functions
Connection helpers include `__test_listen_socket()`, `test_wait_fd()`, `__test_connect_socket()`, `_test_skpair_connect_poll()`, `test_skpair_wait_poll()`, `test_server_run()`, `test_skpair_server()`, `test_client_verify()`, and `test_skpair_client()`. TCP option helpers include `__test_set_md5()`, `test_prepare_key_sockaddr()`, `test_get_one_ao()`, `test_get_ao_info()`, `test_set_ao_info()`, `test_cmp_getsockopt_setsockopt()`, and `test_cmp_getsockopt_setsockopt_ao()`. Counter helpers include `test_get_tcp_counters()`, `test_cmp_counters()`, `test_assert_counters_sk()`, `test_assert_counters_key()`, and `test_tcp_counters_free()`.

## Control Flow
Listen sockets are created nonblocking, bound to `SO_BINDTODEVICE`, bound to a supplied address, and listened on. Connect sockets are made nonblocking and optionally waited to completion unless asynchronous mode is requested. Polling helpers repeatedly call `select()`, inspect `SO_ERROR`, and can stop early when TCP-AO counter deltas meet an expected bitmask or a peer error flag is set. The echo server reads then writes back data; the client sends randomized chunks and verifies byte-for-byte echoes.

## State, Persistence, And Dependencies
No persistent state is stored, but the functions allocate counter/key dumps that callers must free through `test_tcp_counters_free()`. `test_get_tcp_counters()` depends on netstat parsing helpers and Linux TCP-AO UAPI getsockopts. It interprets missing AO info as a socket with no AO state. The code depends on `test_family`, `veth_name`, `this_ip_dest`, constants and macros from `aolib.h`, and kernel UAPI definitions for `TCP_AO_*`, `TCP_MD5SIG_EXT`, and `TCP_INFO`-related counters.

## Integration Points
Higher-level tests use this file as their handshake, traffic generation, and assertion substrate. It bridges direct socket syscalls, TCP-AO UAPI ABI validation, netstat counters, and the thread barrier from `setup.c`.

## Risks
Counter comparison assumes counters never decrease and that key dump order is stable between snapshots. Polling uses short sleeps and global timeouts, so slow systems can produce timeouts that look like protocol failures. `test_cmp_getsockopt_setsockopt()` contains special cases for `cmac(aes128)`/`cmac(aes)` translation and default MAC length, so new algorithm behavior may need updates. Some alloca-based buffers scale with requested test sizes.

## Test Signals
Strong signals include successful nonblocking connects, exact echo verification, AO/MD5 getsockopt fields matching the setsockopt input, expected counter bit deltas, no unexpected `SO_ERROR`, and per-key good/bad counters changing only when requested by the test.
