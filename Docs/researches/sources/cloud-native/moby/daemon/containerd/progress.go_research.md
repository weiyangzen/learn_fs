<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/progress.go -->
# sources/cloud-native/moby/daemon/containerd/progress.go

Purpose: adapts containerd content transfer and snapshot unpack status into Docker-compatible JSON progress messages for pull and push.

Important APIs and flow: `jobs` tracks descriptors by digest and starts a progress goroutine with `showProgress`, calling a `progressUpdater` every 100ms and once more on cancellation. `pullProgress.UpdateProgress` reads active content ingest statuses, emits Downloading/Download complete/Already exists, tracks layers entering snapshot unpack, uses `findMatchingSnapshot` to show Extracting/Pull complete, and removes finished jobs. `pushProgress.UpdateProgress` reads docker status tracker entries and emits Waiting, Unavailable, Mounted from, Layer already exists, Already exists, Pushed, or Pushing. `combinedProgress` runs multiple updaters, and `showBlobProgress` hides small manifest/index/config descriptors while showing layers and unknown large blobs.

State and persistence: in-memory job maps and pull-progress layer/unpack state. Reads content ingest statuses, content info, docker push status tracker, and snapshotter metadata.

Dependencies and integration: used by pull and push. Depends on containerd content/remotes/docker/snapshotters labels, Moby progress output, string ID truncation, and snapshotter append-info labels.

Risks: progress is inherently racy with fast transfers and snapshot commits. `findMatchingSnapshot` requires `containerd.io/snapshot/target`-style annotations added by the pull handler; without them extracting progress is unavailable. The final update has only a 500ms timeout. Hidden layers on already-complete pulls can remove jobs before user sees per-layer status, intentionally matching legacy behavior.

Test signals: no direct tests in this subset; pull/push integration tests would be needed to validate output ordering and status transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/progress.go -->
