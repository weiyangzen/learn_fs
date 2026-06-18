# sources/control-plane/external-snapshotter/pkg/features/features.go

## Purpose
This file declares external-snapshotter feature gates and registers their default specs with Kubernetes' global mutable feature gate.

## Important APIs, Types, And Functions
It defines two `featuregate.Feature` constants: `VolumeGroupSnapshot` (`CSIVolumeGroupSnapshot`) and `ReleaseLeaderElectionOnExit`. The `init` function calls `feature.DefaultMutableFeatureGate.Add(defaultKubernetesFeatureGates)`. The `defaultKubernetesFeatureGates` map sets `VolumeGroupSnapshot` to Beta/default false and `ReleaseLeaderElectionOnExit` to Alpha/default false.

## Control Flow
There is no runtime branching beyond package initialization. Importing the package registers the feature specs with the shared feature gate. Other packages query `utilfeature.DefaultFeatureGate.Enabled(...)` to decide behavior, such as group snapshot support or worker wait group shutdown handling.

## State And Persistence Behavior
The only state change is process-local registration in the default feature gate. No Kubernetes API objects or files are persisted by this package.

## Dependencies And Integration Points
The file depends on `k8s.io/apiserver/pkg/util/feature` and `k8s.io/component-base/featuregate`. `snapshot_controller_base.go` uses `ReleaseLeaderElectionOnExit`, and the controller construction path accepts explicit group snapshot enablement that is conceptually tied to `VolumeGroupSnapshot`.

## Risks
Feature gate registration occurs in `init`, so missing imports can silently prevent feature availability. Both features default to false, so deployments must opt in where needed. Changing default or prerelease state is a compatibility-sensitive API decision.

## Test Signals
No tests are in this file. Behavior is indirectly tested by controller paths that query feature gates or pass group snapshot enablement.
