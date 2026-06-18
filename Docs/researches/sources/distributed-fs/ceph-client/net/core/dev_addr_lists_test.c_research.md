# sources/distributed-fs/ceph-client/net/core/dev_addr_lists_test.c

Purpose: KUnit suite for `struct netdev_hw_addr_list` behavior and the netdevice address-list helpers implemented in `dev_addr_lists.c`. It validates both longstanding primary/secondary address operations and the newer snapshot/reconcile path used by async RX-mode updates.

Important APIs, types, and functions: `struct dev_addr_test_priv` records bitsets of addresses seen, synced, and unsynced by fake driver callbacks. `dev_addr_test_sync()` and `dev_addr_test_unsync()` model hardware programming callbacks. Fixture hooks allocate, register, unregister, and free an Ethernet netdevice. Test cases include `dev_addr_test_basic`, `dev_addr_test_sync_one`, `dev_addr_test_add_del`, `dev_addr_test_del_main`, `dev_addr_test_add_set`, `dev_addr_test_add_excl`, four snapshot-concurrency tests, and `dev_addr_test_snapshot_benchmark`.

Control flow and state: Each test takes RTNL around netdevice operations. Address bytes are simple repeated values so callbacks can map each address to one bit. Tests use `eth_hw_addr_set()`, `dev_addr_set()`, `dev_addr_add()`, `dev_addr_del()`, `dev_uc_add()`, `dev_uc_del()`, `dev_uc_add_excl()`, `__hw_addr_sync_dev()`, `__hw_addr_list_snapshot()`, and `__hw_addr_list_reconcile()` to assert list count, entry address, `sync_cnt`, `refcount`, and callback side effects.

Dependencies and integration points: The suite uses KUnit, Ethernet netdevice allocation, RTNL, and KUnit visibility exports from `dev_addr_lists.c`. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace to reach snapshot and flush helpers that are not general kernel APIs.

Risks covered: The tests explicitly target deleting the primary address, duplicate exclusive adds, tree/list consistency after primary address mutation, stale synced entries, concurrent removal after snapshot sync, concurrent re-add during snapshot unsync, and unrelated concurrent removal while another address is synced. These are the highest-risk state transitions in the address-list implementation.

Risks not fully covered: The suite does not instantiate a real `ndo_set_rx_mode_async` driver, does not exercise `netif_rx_mode_queue()` workqueue lifetime, multicast-specific paths, `__hw_addr_ref_sync_dev()` reference-aware callbacks, allocation failures across all snapshot phases, or lockdep behavior under nested upper/lower device calls.

Test signals: Passing suite name `dev-addr-list-test` is the direct signal. The slow benchmark logs timing for 1024 addresses across 1000 snapshots, useful for catching pathological snapshot cost regressions but not a strict performance assertion.
