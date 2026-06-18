# sources/cloud-native/moby/integration/service/update_test.go

## Purpose
Tests Swarm service update paths for labels, secrets, configs, network attachments, and PIDs limits, including spec persistence and runtime container host config propagation.

## Important APIs, Types, And Functions
- `TestServiceUpdateLabel` mutates `Spec.Labels` through add/remove/add cycles and waits for service version progression.
- `TestServiceUpdateSecrets` and `TestServiceUpdateConfigs` add and remove `SecretReference` or `ConfigReference` entries.
- `TestServiceUpdateNetwork` removes the service network attachment and expects overlay load-balancer endpoints to disappear.
- `TestServiceUpdatePidsLimit` creates and updates `Resources.Limits.Pids` and inspects the task container.
- Helpers `getServiceTaskContainer`, `getService`, `serviceIsUpdated`, and `serviceSpecIsUpdated` encapsulate inspect/poll behavior.

## Control Flow
Tests start a Swarm, create a service, inspect the latest service object, mutate the spec, submit `ServiceUpdate` with the current version, poll for completion or version index change, and re-inspect. The PIDs test carries service ID/state across ordered subtests to exercise create, unset, and update.

## State And Persistence
State includes service versions, update status, labels, secret/config references, network endpoints, and task containers. The network test directly observes `NetworkInspect` container endpoint counts before and after update.

## Dependencies And Integration Points
Depends on Swarm service APIs, network helpers, Moby API types, and poll. It bridges Swarm spec updates to engine task reconciliation and container host config.

## Risks And Edge Cases
All tests skip non-Linux. The PIDs table is order-dependent because later cases update the service created by the first case. Network endpoint counts are sensitive to Swarm load-balancer implementation details. `serviceIsUpdated` requires `UpdateStatus.State == completed`, which depends on Swarm controller status.

## Test Signals
Passing confirms service labels exactly match expected maps, secret/config lists are added then emptied, overlay endpoints are removed after network detachment, and container `HostConfig.Resources.PidsLimit` mirrors nonzero limits while zero unsets it.
