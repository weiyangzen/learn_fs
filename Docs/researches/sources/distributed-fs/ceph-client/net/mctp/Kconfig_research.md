# sources/distributed-fs/ceph-client/net/mctp/Kconfig

Purpose: defines kernel configuration for MCTP core, tests, and optional flow tracking.

Important symbols: `MCTP` is a bool under `NET`. `MCTP_TEST` depends on built-in MCTP and KUnit, defaults with `KUNIT_ALL_TESTS`, and selects `MCTP_FLOWS`. `MCTP_FLOWS` depends on MCTP and selects `SKB_EXTENSIONS`.

Control flow and state: configuration controls whether AF_MCTP core, KUnit tests, and skb extension-backed flow tracking are compiled.

Dependencies and integration: pairs with `net/mctp/Makefile`; tests are included into core C files under `CONFIG_MCTP_TEST`.

Risks and test signals: tests require built-in MCTP (`MCTP=y`) rather than module. `MCTP_FLOWS` changes runtime behavior by attaching key refs to skb extensions, so both enabled and disabled configurations should compile.
