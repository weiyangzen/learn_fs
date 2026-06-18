# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/utils.go

## Purpose
This dashboard utility subpackage contains pod classifiers, mount label selectors, PVC/target ID helpers, websocket log piping, and app-pod desensitization.

## Important APIs, Types, And Functions
Key functions are `IsAppPod`, `IsMountPod`, `IsSysPod`, `IsCsiNode`, `IsAppPodShouldList`, `LabelSelectorOfMount`, `GetUniqueOfPVC`, `GetTargetUID`, `NewLogPipe`, `LogPipe.Write`, `LogPipe.Read`, `DesensitizeAppPod`, and `desensitizeContainer`.

## Control Flow
Classifiers inspect labels for JuiceFS app, mount, system, and CSI-node pods. `IsAppPodShouldList` follows pod PVC volumes to PVCs/PVs and admits pods using JuiceFS CSI PVs or unbound PVCs. `GetTargetUID` parses kubelet CSI mount paths from annotation values. `NewLogPipe` starts a goroutine that reads websocket messages, closes the stream on disconnect, and responds to ping with pong. Desensitization copies selected pod metadata/status/spec fields and strips non-mount containers down to operational fields.

## State And Persistence
All helpers are stateless except `LogPipe`, which owns a websocket connection and stream for the lifetime of a request. No persistent state is written.

## Dependencies And Integration Points
These helpers are used across pod/PV handlers and cached services. They depend on Kubernetes core/meta/label types, controller-runtime client, `common` labels, and util helpers.

## Risks
`IsAppPodShouldList` returns false on the first PVC/PV get error, which can hide otherwise valid app pods. `LabelSelectorOfMount` duplicates package-level dashboard logic and can drift. Desensitization copies ObjectMeta wholesale, so labels/annotations remain visible even while container details are reduced.

## Test Signals
No tests are in this file directly. Related tests cover the package-level selector/sort utilities, not these subpackage classifiers or websocket behavior.
