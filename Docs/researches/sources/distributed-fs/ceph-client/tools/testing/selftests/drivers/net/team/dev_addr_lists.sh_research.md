# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/dev_addr_lists.sh

Purpose: Regression-tests team device cleanup of unicast/multicast address lists using shared LAG cleanup logic.

Important APIs/functions: Sources forwarding `lib.sh` and bonding `lag_lib.sh`. Defines `destroy`, `cleanup`, and `team_cleanup`; `team_cleanup` delegates to `test_LAG_cleanup "team" "lacp"`.

Control flow: The script installs cleanup trap, runs `tests_run` for the single `team_cleanup` test, and exits with `EXIT_STATUS`. Cleanup deletes expected devices (`dummy1`, `dummy2`, `team0`, `mv0`) and runs `pre_cleanup`.

State and persistence: Creates and deletes LAG/team-related dummy/macvlan/team devices through the shared helper. No namespaces are used in this wrapper.

Dependencies and integration: Requires team driver support, forwarding test infrastructure, bonding LAG helper, and iproute2. The helper likely exercises address-list propagation and cleanup.

Risks: Most behavior is hidden in `lag_lib.sh`; this wrapper is thin and assumes device names used by the helper. Cleanup deletes fixed names, so concurrent tests using those names would conflict.

Test signals: PASS is `test_LAG_cleanup` succeeding for team/lacp and cleanup leaving no stale address-list devices.
