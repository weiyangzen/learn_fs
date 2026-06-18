# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup.go

Purpose: Provides Linux netlink helper functions for macvlan link creation, mode mapping, VLAN subinterface management, dummy parent link management, and dummy name derivation.

Important APIs and functions: `createMacVlan` maps mode strings to netlink constants, verifies the parent, and creates `netlink.Macvlan`. `setMacVlanMode` maps private/vepa/bridge/passthru. `parentExists`, `createVlanLink`, `delVlanLink`, `parseVlan`, `createDummyLink`, `delDummyLink`, and `getDummyName` implement parent link support.

Control flow: VLAN creation parses `parent.vlan`, validates VLAN ID 1-4094, creates and brings up the VLAN link. Delete verifies the link is a slave before removal. Dummy deletion verifies `ParentIndex == 0`.

State and persistence: mutates only Linux link state; persistence is handled by network/store code.

Dependencies and integration points: used by macvlan network and join paths; depends on `vishvananda/netlink` and `ns.NlHandle`.

Risks: netlink operations are not transactional. `createDummyLink` has an unused second parameter. Real parent and VLAN operations need privilege.

Test signals: `macvlan_setup_test.go` covers validation and mode mapping, not actual link creation/deletion.
