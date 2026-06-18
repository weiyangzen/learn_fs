<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull.go -->
# sources/cloud-native/cri-o/server/image_pull.go

## Purpose

This file implements CRI `PullImage`, including authentication handling, concurrent pull deduplication, namespace-specific policy/auth context, decryption keys, optional separate cgroup pulls, progress timeout/metrics, artifact fallback, and Docker auth decoding.

## Important APIs, Types, and Functions

`PullImage` prepares `pullArguments` and deduplicates in-progress pulls through `pullOperationsInProgress`. `pullImage` creates a namespace-aware image system context, handles namespaced auth files, chooses cgroup settings, resolves short names, and tries pull candidates. `contextForNamespace`, `prepareTempAuthFile`, `pullImageCandidate`, `resolveImageRefToID`, `consumeImagePullProgress`, `tryIncrementImagePullFailureMetric`, `tryRecordSkippedMetric`, and `decodeDockerAuth` support the flow.

## Control Flow

The RPC extracts image, sandbox cgroup, namespace, and auth. Docker `auth` is base64-decoded into username/password if present. A locked map ensures only one goroutine pulls a specific `pullArguments` tuple while others wait on its waitgroup. The active pull uses namespace signature policy, optionally consumes a namespaced credential-provider auth file by renaming it into an `in-use` directory and cleaning it after pull, applies explicit credentials, reads decryption config, validates separate-pull-cgroup systemd requirements, resolves short-name candidates, and pulls each candidate until one succeeds. Candidate pulls set up a progress channel and cancellation goroutine that cancels when no progress arrives within configured timeout. Successful pulls increment success metrics and resolve the pulled repo digest to a storage image ID or artifact CRI ID.

## State and Persistence Behavior

State includes the in-memory pull operation map, `storage.ImageBeingPulled`, metrics counters/histograms, temporary namespaced auth-file moves/removals, pulled image/artifact storage, and optional cgroup creation in storage copy options. The panic guard initializes pull errors so waiters do not observe a false success after panic.

## Dependencies and Integration Points

The file integrates with CRI auth and sandbox config, containers/image system context and progress types, CRI-O credential provider auth file naming, storage image server pull/status APIs, artifact store status, ocicrypt decryption keys, registry error descriptors, metrics, signature policies, short-name resolution, and systemd cgroup configuration.

## Risks and Edge Cases

Deduplication key includes credentials, namespace, cgroup, and image, so similar pulls with different auth are separate. Namespaced auth file consumption intentionally races for same normalized image names; kubelet retry is expected to recover. Progress timeout begins only after progress events because the timer is initially stopped. `decodeDockerAuth` treats malformed decoded strings without `:` as empty credentials. Separate pull cgroup is systemd-only and validates `.slice` names except pod cgroup mode. Artifact resolution after pull depends on artifact store status if image storage lookup fails.

## Test Signals

Tests cover successful pull returning image ID, credential decode errors, pull errors, and short-name resolution errors. Additional coverage should include concurrent deduplication, namespaced auth file movement/cleanup, progress timeout cancellation, artifact ID resolution, metrics labels, and separate cgroup validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_pull.go -->
