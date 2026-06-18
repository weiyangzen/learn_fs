# sources/control-plane/rook/pkg/daemon/multus/image-pull-daemonset.yaml

Purpose: template for image-puller DaemonSets used to pre-pull the Nginx image and discover how many nodes match each configured node type.

Important APIs/types/functions: embedded as `imagePullDaemonSet` and rendered by `generateImagePullDaemonSet()` from `imagePullTemplateConfig`. Labels include app and node type for expected-count calculations.

Control flow: `startImagePullers()` creates one DaemonSet per node type at the start of validation. The state machine lists these DaemonSets, waits for scheduled counts to stabilize, verifies no node type overlap, then waits for all puller pods to run before deleting the puller DaemonSets.

State and persistence behavior: resources are temporary and owner-referenced to the validation owner ConfigMap. Their scheduled pod counts become in-memory expected-count state used later to calculate host checker and client expectations.

Dependencies and integration points: depends on Kubernetes DaemonSet scheduling, node selector/toleration correctness, and image pull success. It intentionally does not attach Multus networks, so failures isolate Kubernetes/image issues.

Risks: overlapping node type placements are detected later by pod node names, not by template rendering. Read-only root filesystem and non-root security context rely on image compatibility. If image pullers cannot schedule, validation cannot infer expected client counts.

Test signals: indirect unit coverage for per-node type count helpers in `resources_test.go`; no direct YAML rendering assertions.
