# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup_test.go

Purpose: Tests macvlan setup helper validation and mode mapping.

Important APIs and functions: `TestValidateLink` checks `parentExists`. `TestValidateSubLink` checks valid and invalid VLAN naming/parent cases. `TestSetMacVlanMode` checks bridge, passthru, private, vepa, invalid, and empty mode conversions.

Control flow: direct assertions on helper return values and netlink constants.

State and persistence: reads interface existence; no datastore and no link creation.

Dependencies and integration points: verifies `macvlan_setup.go` helper behavior against `netlink` constants.

Risks: depends on loopback interface existing. Does not cover privileged netlink mutations or dummy-name generation.

Test signals: focused validation coverage for setup helper pure logic.
