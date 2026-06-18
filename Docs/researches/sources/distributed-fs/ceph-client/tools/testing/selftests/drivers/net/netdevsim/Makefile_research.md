# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/Makefile

Purpose: Registers the netdevsim driver selftests with the kselftest build/run harness.

Important APIs/variables: `TEST_PROGS` lists executable test programs for devlink, ethtool, FIB, nexthop, peer, psample, qdisc visibility, and UDP tunnel offload coverage. `TEST_FILES` declares the shared helper `ethtool-common.sh`. `include ../../../lib.mk` imports kselftest install and run rules.

Control flow: There is no runtime logic. During `make` or kselftest installation, `lib.mk` consumes these variables to copy scripts into the test output and run `TEST_PROGS` as separate tests.

State and persistence: No state is created by the Makefile itself. It only determines which files are installed and therefore which scripts can be invoked by the harness.

Dependencies and integration: Integrates this directory with Linux kselftest. It assumes each listed script is self-contained or includes declared helper files. Kernel feature requirements are expressed separately in `config`.

Risks: A script omitted from `TEST_PROGS` will not run in normal kselftest flows. A helper omitted from `TEST_FILES` may be missing from installed test trees. Ordering is mostly independent, but many scripts require root and mutable netdevsim state.

Test signals: Build/install output should include every listed program and `ethtool-common.sh`; kselftest runners should discover the same program set.
