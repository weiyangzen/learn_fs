# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup.go

Purpose: Provides Linux netlink helper functions for creating ipvlan interfaces, validating modes/flags, creating/deleting VLAN subinterfaces, creating/deleting dummy parent links, and deriving dummy names.

Important APIs and functions: `createIPVlan` maps mode and flag strings to netlink constants, verifies the parent, and creates `netlink.IPVlan`. `setIPVlanMode` maps `l2`, `l3`, `l3s`. `setIPVlanFlag` maps `bridge`, `private`, `vepa`. `parentExists` probes `ns.NlHandle`. `createVlanLink`/`delVlanLink` manage `parent.vid` links. `parseVlan` validates `name.vlan_id`. `createDummyLink`/`delDummyLink` manage dummy parent links. `getDummyName` returns `di-` plus a truncated network id.

Control flow: helpers generally validate naming and parent existence before mutating netlink state. VLAN IDs are restricted to 1-4094. Delete helpers avoid deleting parent devices by checking `ParentIndex`.

State and persistence: no datastore state; all effects are Linux netlink link creation, link up, or deletion.

Dependencies and integration points: used by ipvlan network and join code; depends on `vishvananda/netlink` through `ns.NlHandle`.

Risks: helper names and comments mention macvlan in a few error comments, but behavior is ipvlan. `createDummyLink` has an unused `truncNetID` parameter. Netlink operations require privilege and are not transactional.

Test signals: `ipvlan_setup_test.go` covers parent existence, VLAN parsing errors, mode mapping, and flag mapping.
