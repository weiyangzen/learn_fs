# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/Makefile

Purpose: Build/install manifest for bonding driver selftests.

Important APIs/variables: `TEST_PROGS` for executable tests, `TEST_FILES` for reusable topology/library files, `TEST_INCLUDES` for shared net/forwarding/netconsole helpers, and inclusion of `../../../lib.mk`.

Control flow: The manifest registers bonding behavior/regression tests including ARP interval panic, LACP, IPsec offload, macvlan/ipvlan over bond, option matrix tests, passive LACP, stacked header parsing, dev address lists, recovery updelay, and netconsole-over-bonding.

State and persistence: Build/install only. Runtime state is created by individual scripts.

Dependencies and integration points: Integrates bonding tests with common `net/lib.sh`, forwarding helpers, and netconsole helper scripts.

Risks and test signals: Missing helper files break many tests. Incorrect `TEST_FILES` classification would omit topology libraries needed at runtime.
