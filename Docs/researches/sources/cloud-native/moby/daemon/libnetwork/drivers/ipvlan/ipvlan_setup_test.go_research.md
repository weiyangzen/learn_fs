# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup_test.go

Purpose: Unit tests ipvlan setup helpers for interface existence, VLAN name parsing, mode conversion, and flag conversion.

Important APIs and functions: `TestValidateLink` checks `parentExists` on loopback and a fake interface. `TestValidateSubLink` checks valid `lo.10` and invalid formats/nonexistent parent. `TestSetIPVlanMode` checks l2/l3/l3s and invalid/empty modes. `TestSetIPVlanFlag` checks bridge/private/vepa and invalid/empty flags.

Control flow: tests are direct function calls with expected errors and netlink constants.

State and persistence: reads host loopback link; no datastore. It does not create links.

Dependencies and integration points: depends on `netlink` constants and the setup helper implementations.

Risks: uses real namespace `lo`, so unusual test environments without loopback would fail. Does not test actual link creation/deletion.

Test signals: good coverage for pure validation and mapping logic, weaker coverage for privileged netlink mutations.
