<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml

## Purpose
Namespaced Role allowing controller-runtime leader election.

## Important APIs, Types, And Functions
Grants full get/list/watch/create/update/patch/delete on ConfigMaps and Leases plus create/patch on events.

## Control Flow
Manager uses these permissions when `--leader-elect` is enabled.

## State And Persistence
Leader election records persist as ConfigMaps or Leases in the operator namespace.

## Dependencies And Integration Points
Bound to the controller-manager service account by `leader_election_role_binding.yaml`.

## Risks And Edge Cases
Permissions are broad for ConfigMaps but scoped to namespace. Lost permissions prevent manager startup leadership.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml -->
