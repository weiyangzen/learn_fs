<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/selftest.c

Purpose: runs optional Bluetooth subsystem selftests at initialization time, including ECDH P-256 test vectors and SMP selftests, with a debugfs result file for the ECDH test when enabled.

Important APIs/types/functions: under `CONFIG_BT_SELFTEST_ECDH`, static test vectors define private keys, public keys, and expected DH keys for three ECDH cases. `test_ecdh_sample` sets a private key and computes both sides of a shared secret. `test_ecdh` allocates the `ecdh-nist-p256` KPP transform, runs samples, records duration, and creates debugfs file `selftest_ecdh`. `run_selftest` calls `test_ecdh` and `bt_selftest_smp`. `bt_selftest` or `bt_selftest_init` dispatches the run depending on whether Bluetooth is modular or built-in.

Control flow: when selftesting is compiled in, initialization logs start, runs ECDH if configured, aborts on ECDH failure, then runs SMP selftests, logs finish, and returns the first error. Built-in Bluetooth schedules selftests via `late_initcall` so Bluetooth and crypto init ordering does not clash. Modular Bluetooth exposes `bt_selftest` for module init. ECDH debugfs reads return a cached `PASS (<usecs>)` or `FAIL` string.

State and persistence behavior: test vectors are `__initconst`; ECDH helper functions are `__init`. The only persistent runtime artifact is `test_ecdh_buffer` and the debugfs file, both representing the latest boot/module-load selftest result. The tests do not persist secrets or alter controller state.

Dependencies and integration points: depends on Linux crypto KPP `ecdh-nist-p256`, Bluetooth ECDH helpers, SMP selftest implementation in `smp.c`, `bt_debugfs`, debugfs file operations, kernel time accounting, and Bluetooth init/module mode.

Risks: failures in crypto allocation or ECDH vector comparison can fail Bluetooth selftest initialization. The ECDH transform is freed on the success path but not explicitly freed on early failure after allocation in this snapshot, which is a leak risk during failing init. Debugfs creation assumes `bt_debugfs` is usable. Test coverage is compile-time gated, so many builds may not run these checks.

Test signals: enable `CONFIG_BT_SELFTEST` and `CONFIG_BT_SELFTEST_ECDH`, boot or load the module, check kernel logs for pass/fail and `/sys/kernel/debug/bluetooth/selftest_ecdh` for result text. Negative testing can force bad vectors or missing crypto algorithm to verify failure propagation. SMP selftest logs/results provide the second major signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.c -->
