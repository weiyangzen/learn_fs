## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/regression_pidfd_setns_test.c

**Purpose:** Regression coverage for a pidfd `setns()` active-reference race described in the file comments: if the target task exits between namespace-set preparation and commit, active refs could be mishandled.

**Important APIs and flow:** Both tests use `create_child()` from the pidfd helpers to obtain a pidfd. `simple_pidfd_setns` creates a child that unshares UTS, IPC, NET, and USER namespaces, signals readiness over a socketpair, exits, and lets the parent call `setns(pidfd, CLONE_NEWUTS | CLONE_NEWIPC)`. `simple_pidfd_setns_clone` creates the child with namespace clone flags directly and calls `setns()` while the child sleeps. `SIGCHLD` is ignored for autoreap.

**State, dependencies, integration:** State is the pidfd, target task namespace set, and child lifetime. It depends on pidfd selftest helpers and `setns()` pidfd support. It integrates with namespace set preparation/commit and active-ref acquisition paths.

**Risks and test signals:** The tests log `setns()` return values but do not assert success, because the regression signal is kernel warnings or refcount failures rather than user-space return alone. Environment restrictions on user/net namespace creation can affect the path. Passing without kernel splats signals pidfd namespace switching no longer resurrects or underflows active refs incorrectly.
