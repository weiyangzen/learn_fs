# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fdb_notify.sh

Purpose: this script checks that FDB add/delete operations generate a single notification, not duplicates, for bridge, VXLAN, and macvlan self/master paths.

Important APIs and functions: it sources `lib.sh`, uses `tests_run`, deferred cleanup helpers (`defer`, `defer_scope_push`, `defer_scope_pop`, `defer_scopes_cleanup`), `bridge monitor fdb`, `bridge fdb add/del`, and `adf_ip_link_add` / `adf_ip_link_set_master` helper wrappers.

Control flow: `do_test_dup` starts `bridge monitor fdb` into a temporary file, performs the requested FDB operation for MAC `00:11:22:33:44:55` and VLAN 1, stops the monitor through deferred cleanup, counts matching lines, and asserts exactly one notification. Test cases create the required topology, then call `do_test_dup` for add and delete on bridge self, VXLAN self, VXLAN master, macvlan self, and macvlan attached to a bridge.

State and persistence: it creates transient bridge, VXLAN, dummy, and macvlan devices through helper functions and temporary monitor output files. Deferred cleanup removes temp files and processes; final trap drains deferred scopes.

Dependencies and integration points: depends on bridge, VXLAN, macvlan, dummy devices, `bridge monitor`, and lib.sh advanced deferred fixture helpers. It integrates with the generic `tests_run` dispatcher through `ALL_TESTS`.

Risks and test signals: monitor startup is synchronized only by `sleep 0.5`, and notification delivery is observed after another fixed sleep, so very slow environments can be flaky. Strong signal is exactly one occurrence of the test MAC in the monitor log for each operation.
