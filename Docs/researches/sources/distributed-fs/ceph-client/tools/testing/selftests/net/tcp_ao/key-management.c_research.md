# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/key-management.c

Purpose: this is the main TCP-AO key lifecycle test. It verifies adding, deleting, selecting, rotating, matching, dumping, and counter-accounting for AO master key tuples on closed, listening, and established sockets, including current-key and rnext-key behavior.

Important APIs and types: it uses `TCP_AO_ADD_KEY`, `TCP_AO_DEL_KEY`, `TCP_AO_INFO`, `TCP_AO_GET_KEYS`, `TCP_AO_REPAIR`, VRF helpers, ftrace expectations, and counter helpers. `struct test_key` models password, algorithm, client/server key IDs, MAC length, match flags, current/rnext flags, and expected counter usage. `struct key_collection` owns the generated key set. Important functions include `setup_vrfs`, `prepare_sk`, `test_del_key`, `try_delete_key`, `test_set_key`, `check_closed_socket`, `check_listen_socket`, `init_default_key_collection`, `key_collection_socket`, `verify_keys`, `verify_counters`, `start_server`, `run_client`, `try_unmatched_keys`, `check_current_back`, and `roll_over_keys`.

Control flow: the client thread first tests closed sockets and listen sockets, then established sockets. The server thread runs matching established scenarios in parallel. Tests cover deletion of ordinary/current/rnext keys, forced replacement during deletion, rejection of current/rnext changes on listeners, restriction of AO repair on listeners, current/rnext setup before connect, peer rnext requests that rotate current keys, rotation across 20 keys, and established-socket pruning of nonmatching address or VRF keys.

State and persistence: large transient state is stored in `collection.keys`; per-key flags are updated to indicate expected transmit use and skipped counter checks. Kernel state includes AO keys, AO info current/rnext fields, optional VRF route/device state, and per-key counters. FIPS mode is cached from `/proc/sys/crypto/fips_enabled` and removes non-FIPS algorithms from generation.

Dependencies and integration points: relies on TCP-AO, optional VRF, optional ftrace tracepoints, crypto algorithms, and all shared aolib socket/counter/topology helpers. The Makefile builds it for IPv4 and IPv6. It uses `TEST_WRONG_IP` and `TEST_NETWORK` macros for address-family-specific negative matching.

Risks: the test has intentional `test_xfail` paths for some listener current/rnext deletion behavior, so not every surprising result is a hard failure. Randomized key material and algorithm selection can make failures hard to reproduce unless the random seed is controlled by the broader harness. VRF-specific coverage is skipped when VRF support is absent.

Test signals: success emits 121 planned test results across key deletion, listener restrictions, key dumps, current/rnext verification, data-transfer survival, key rotation, counter assertions, and trace expectations. Failures identify the scenario name and key tuple details.
