# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_topo_3d1c.sh

Purpose: Extends the two-downlink topology to three server downlinks for bonding option tests.

Important APIs/functions: Sources `bond_topo_2d1c.sh`, overrides `setup_prepare()`, appends `mac[2]`, creates `eth2`/`s2`, enslaves it to `bond0`, and attaches TC clsact to gateway side `s2`.

Control flow: The overridden setup calls base gateway/server/client creation, then adds the third veth pair between server and gateway bridge. Base cleanup dynamically counts `eth*` links, so it removes the extra slave too.

State and persistence: Adds one extra MAC and transient veth/TC state. No persistent files.

Dependencies and integration points: Used by `bond_options.sh` for three-slave failover, priority, and GARP scenarios.

Risks and test signals: The helper relies on base functions counting links in real time; if link names differ, cleanup/reset behavior can break downstream tests.
