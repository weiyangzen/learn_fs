
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_pull.go

## Purpose

This file implements CRI image pulling, registry authentication and mirror configuration, CRI-managed image reference creation, image-store refresh, image pull metrics, encrypted image pull options, snapshotter selection, and progress-timeout reporters for both local `client.Pull` and containerd transfer-service pulls.

## Important APIs, Types, and Functions

Public and high-value functions include `(*GRPCCRIImageService).PullImage`, `(*CRIImageService).PullImage`, `pullImageWithLocalPull`, `pullImageWithTransferService`, `ParseAuth`, `createOrUpdateImageReference`, `getLabels`, `UpdateImage`, `hostDirFromRoots`, `registryHosts`, `toRuntimeAuthConfig`, `defaultScheme`, `addDefaultScheme`, `registryEndpoints`, `encryptedImagesPullOpts`, `snapshotterFromPodSandboxConfig`, and `newCRICredentials`.

Progress-related types include `pullProgressReporter`, `pullRequestReporter`, `pullRequestReporterRoundTripper`, `countingReadCloser`, and `transferProgressReporter`.

## Control Flow

The gRPC handler builds a credential callback from request auth or host config and delegates to `CRIImageService.PullImage`. The service increments in-progress metrics, normalizes the image reference with Docker reference parsing, parses the configured progress timeout, selects a snapshotter from the runtime handler or deprecated sandbox annotation, prepares CRI labels including pinned-image labels, and chooses either local pull or transfer service based on config.

The local pull path creates a Docker resolver with CRI registry hosts and a progress-reporting HTTP client wrapper, then calls `client.Pull` with resolver, snapshotter, unpack, labels, concurrency, download limiter, unpack duplication suppressor, syncfs, optional encrypted-image unpack options, optional snapshot annotations, and optional child-label filtering for discarded unpacked layers. The transfer path constructs a transfer image store with platform/unpack/labels, creates a registry with CRI credentials, headers, and host config path, starts transfer progress reporting, calls `transferrer.Transfer`, and then resolves the image from containerd.

After a successful pull, the service obtains the config digest as image ID, computes repo tag and repo digest, creates or updates references for image ID, tag, and digest, refreshes the CRI image store for each, records throughput, logs, and returns the image ID. `UpdateImage` reconciles containerd image events, adding CRI-managed labels and an ID reference when needed before updating the in-memory store.

## State and Persistence Behavior

Successful pulls persist image metadata references in containerd's image store, unpack snapshots through the selected snapshotter, and update the CRI in-memory image store. Metrics counters, gauges, and histograms are updated around the pull. Progress reporters maintain in-memory counters and cancel the pull context when active requests stop making byte progress. No direct content deletion occurs except via child GC label configuration when discarding unpacked layers.

## Dependencies and Integration Points

Dependencies include containerd client pull APIs, image/content stores, transfer service, Docker resolver/config, registry credential helper, image encryption, CRI config, CRI labels and annotations, tracing, metrics, platform selection, snapshotter helpers, distribution reference parsing, and CRI runtime API. The file is central to kubelet `PullImage`, startup image cache recovery, and image event reconciliation.

## Risks and Edge Cases

The comments document a fundamental split between containerd metadata/content and CRI's ready-only in-memory index. Failed pulls can leave containerd metadata not represented as CRI-ready. `createOrUpdateImageReference` is not atomic across create/get/update and can race with external deletion. Transfer service currently lacks support for several local-pull options noted in TODOs. Progress timeout logic must distinguish idle periods from active no-progress requests. Auth matching depends on parsed `ServerAddress` host and ignores registry token. Snapshotter selection still supports a deprecated annotation fallback.

## Test Signals

Tests cover auth forms and server matching, mirror endpoint defaults and wildcard precedence, default scheme selection, encrypted pull option count, runtime-handler snapshotter selection and annotation fallback, pinned labels, transfer progress accounting and timeout, and local pull progress cancellation semantics. Integration tests are still needed for actual pull/unpack/reference behavior across local and transfer paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull.go -->
