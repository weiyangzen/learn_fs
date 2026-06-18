# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/config

Purpose: this kselftest config fragment documents kernel options needed for the TCP-AO selftests. It enables TCP-AO, supporting crypto algorithms, namespace/VRF infrastructure, tracepoints, IPv6 routing tables, TCP-MD5, and veth.

Important entries: `CONFIG_TCP_AO=y` is the primary feature. `CONFIG_TCP_MD5SIG=y` supports MD5 comparison tests. `CONFIG_CRYPTO_CMAC`, `CONFIG_CRYPTO_HMAC`, `CONFIG_CRYPTO_RMD160`, and `CONFIG_CRYPTO_SHA1` cover algorithms used by key tests. `CONFIG_IPV6` and `CONFIG_IPV6_MULTIPLE_TABLES` support IPv6 variants. `CONFIG_NET_L3_MASTER_DEV`, `CONFIG_NET_VRF`, and `CONFIG_VETH=m` support test topology and VRF coverage. `CONFIG_TRACEPOINTS=y` enables ftrace event validation.

Control flow: this is declarative data consumed by kselftest build/config tooling rather than executable code. It does not include conditionals or generated state.

State and persistence: the file persists desired kernel config symbols in the source tree. It does not change the running kernel; it informs configuration checks and build/test environments.

Dependencies and integration points: maps directly to runtime probes in `lib/kconfig.c` and skip messages in `aolib.h`. Missing required symbols cause test skips or failures depending on the helper and feature.

Risks: the fragment is not exhaustive for every algorithm used in `key-management.c`, which also references SHA-2, SHA-3, MD5, and AES-CMAC behavior through crypto names. Runtime FIPS mode can still disable non-FIPS algorithms even when symbols exist. `CONFIG_VETH=m` requires the module to be loadable in the test environment.

Test signals: indirect signal is reduced skip count from `kernel_config_has()` probes and successful execution of TCP-AO, TCP-MD5, VRF, veth, IPv6, and tracepoint tests.
