# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_ipsec_offload.sh

Purpose: Validates XFRM/IPsec offload lifecycle when traffic traverses a bond, especially offload migration/removal on active slave changes.

Important APIs/functions: `active_slave_changed()`, `test_offload()`, `setup_env()`, `setup_bond()`, `ip xfrm state/policy`, bond active-backup setup, netns/veth/dummy or netdevsim-style links, and `check_fail`/`check_err`.

Control flow: The script creates namespaces and a bond topology, configures IPsec SAs/policies with offload on a bond/slave path, verifies traffic/offload behavior, changes active slave state, retests, and then deletes the bond while checking that security associations are removed from the driver.

State and persistence: Mutates netns links, XFRM state/policy, and bond slave state; cleanup removes transient kernel objects.

Dependencies and integration points: Requires bonding, XFRM user API, ESP offload support, veth/dummy/netdevsim-style devices, and iproute2 XFRM offload syntax.

Risks and test signals: Failures indicate stale driver offload SAs, active slave transition bugs, or incorrect offload binding to the bond/slave.
