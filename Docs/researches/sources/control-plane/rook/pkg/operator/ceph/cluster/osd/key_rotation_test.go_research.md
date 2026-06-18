# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation_test.go

## Purpose
This file tests small but safety-relevant helpers from `key_rotation.go`: stable CronJob naming and same-node placement mutation for key rotation jobs.

## Important APIs and Tests
`Test_keyRotationCronJobName` verifies that OSD IDs 0 and 1 are formatted with `keyRotationCronJobAppNameFmt`. `Test_applyKeyRotationPlacement` provides pod specs with existing affinity, anti-affinity, and topology spread constraints, plus a case with nil affinity. It calls `applyKeyRotationPlacement()` and asserts anti-affinity and topology spread constraints are removed while required pod affinity is set to the supplied labels and hostname topology key.

## Control Flow Covered
The placement test covers both branches of affinity initialization: existing `Affinity` and nil `Affinity`. It also verifies that prior scheduling constraints are intentionally cleared. This is important because key rotation must run on the same node as the target OSD and should not inherit constraints that could prevent that.

## State and Persistence Behavior
The test uses in-memory `v1.PodSpec` values only. It does not create CronJobs or persist Kubernetes objects.

## Dependencies and Integration Points
The tests use Kubernetes core API structs and `testify/assert`. They indirectly protect the CronJob builder because `getKeyRotationPodTemplateSpec()` calls `applyKeyRotationPlacement()` after global and device-set placement application.

## Risks and Gaps
The tests do not cover `getKeyRotationContainer()`, Vault TLS volume wiring, device list construction, host path construction, Multus/host networking, schedule defaulting, owner references, deletion when disabled, or filtering to encrypted PVC-backed OSDs. Since the covered helper intentionally removes topology spread and anti-affinity, any future change to placement layering should add tests here.

## Test Signals
The file is a narrow regression signal. It protects the scheduling invariant that rotation jobs must be co-located with their OSDs, which is the highest-risk small helper in the key-rotation path.
