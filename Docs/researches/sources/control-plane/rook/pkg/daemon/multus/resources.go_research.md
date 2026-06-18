# sources/control-plane/rook/pkg/daemon/multus/resources.go

Purpose: implements Kubernetes resource creation, inspection, expected-count tracking, and cleanup helpers for the Multus validation test.

Important APIs/types/functions: `podNetworkInfo` records web server node/public/cluster addresses. `createOwningConfigMap()` creates the owner ConfigMap used as a garbage-collection root. `startWebServer()`, `getWebServerInfo()`, `startImagePullers()`, `startHostCheckers()`, and `startClients()` create or inspect validation resources. `perNodeTypeCount` plus `Increment()`, `Total()`, and `Equal()` model scheduled counts. `getImagePullPodCountPerNodeType()`, `ensureOneImagePullPodPerNode()`, `getNumRunningPods()`, `numPodsReadyWithLabel()`, `getPodsWithLabel()`, and `cleanUpTestResources()` support state-machine polling and cleanup.

Control flow: the validation run first creates an owner ConfigMap, then the web server and image pullers. Image puller DaemonSet status establishes the expected number of nodes per node type. Host checker and client DaemonSets are generated per node type, with expected pod counts derived from image-puller scheduling. Cleanup deletes the owner ConfigMap with foreground propagation, best-effort deletes client pods, and polls until the owner disappears.

State and persistence behavior: all validation resources are owner-referenced to a single ConfigMap named `multus-validation-test-owner`; deletion of that ConfigMap is the intended cleanup mechanism. `perNodeTypeCount` is in-memory state passed through validation states. Resource status is read from Kubernetes DaemonSets and Pods.

Dependencies and integration points: uses Kubernetes typed clients for CoreV1 and AppsV1, API errors, owner references, DeleteCollection, and polling utilities. It depends on template generation functions in `templates.go` and pod/network helpers in `util.go`.

Risks: creating a fixed owner ConfigMap name means only one validation run per namespace can proceed; stale resources block later runs. `ensureOneImagePullPodPerNode()` detects overlapping node type definitions only after pods exist. Cleanup's best-effort client pod deletion uses foreground delete options with default grace for the owner, and CNI IPAM exhaustion is a noted concern. `getImagePullPodCountPerNodeType()` requires exactly one DaemonSet per node type and nonzero scheduling.

Test signals: `resources_test.go` covers `perNodeTypeCount` helper behavior. Resource creation, cleanup, owner references, and Kubernetes API interactions are not directly unit tested in this file's companion test.
