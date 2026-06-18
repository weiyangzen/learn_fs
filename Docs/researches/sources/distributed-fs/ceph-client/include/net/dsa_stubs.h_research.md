# sources/distributed-fs/ceph-client/include/net/dsa_stubs.h

Read `sources/distributed-fs/ceph-client/include/net/dsa_stubs.h` completely for this pass (48 lines, 1314 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dsa_stubs.h_research.md`.

Purpose: provides a small DSA stub interface for code outside the DSA core to call optional DSA functionality, currently conduit hardware timestamp validation, while still compiling cleanly when DSA is disabled.

Important APIs/types/functions: with `CONFIG_NET_DSA`, `struct dsa_stubs` contains `conduit_hwtstamp_validate()`, and `extern const struct dsa_stubs *dsa_stubs` points to registered DSA core stubs. `dsa_conduit_hwtstamp_validate()` checks `netdev_uses_dsa()`, asserts RTNL, and delegates to the DSA stub. Without DSA, the inline helper returns zero.

Control flow: netdevice timestamping configuration code can call `dsa_conduit_hwtstamp_validate()`. Non-DSA devices immediately succeed. DSA conduit devices are validated by DSA core while RTNL prevents stubs from being unregistered concurrently with conduit teardown.

State and persistence: the only state is the global stub table pointer while DSA core is loaded. No per-device state is stored here.

Dependencies and integration points: depends on netdevice, net timestamp config, DSA core, RTNL locking, and `netdev_uses_dsa()` from `dsa.h`.

Risks: callers must hold RTNL for DSA devices. The helper silently succeeds for non-DSA and disabled DSA builds. Stub pointer lifetime is safe only under the documented RTNL condition.

Test signals: compile with and without DSA; validate timestamp config on normal and DSA conduit devices; assert RTNL coverage; unload DSA core after conduit teardown; verify disabled builds do not reject timestamp settings.
