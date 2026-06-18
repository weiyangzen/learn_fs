# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/Makefile

Purpose: Registers team driver selftest scripts and shared includes with kselftest.

Important APIs/variables: `TEST_PROGS` lists team tests for decoupled enablement, address list cleanup, non-Ethernet header ops, options, propagation, refleak, active-backup teamd, and transmit failover. `TEST_INCLUDES` installs `team_lib.sh`, bonding `lag_lib.sh`, forwarding libs, namespace helpers, and defer helpers. `include ../../../lib.mk` wires into kselftest.

Control flow: No runtime flow; `lib.mk` uses the variables during build/install/run.

State and persistence: The Makefile creates no state. It determines test discovery and helper availability in installed selftest trees.

Dependencies and integration: Depends on team and bonding shell libraries and Linux kselftest conventions.

Risks: Missing helper entries can cause installed-tree failures even if source-tree runs work. Adding a new team test requires updating `TEST_PROGS`.

Test signals: Kselftest install should copy all programs and includes, and test runners should discover the listed programs.
