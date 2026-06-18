# sources/cloud-native/cri-o/server/utils.go

## Purpose
Shared server helpers for label validation, environment merging, image decryption keys, mount source resolution, context-error detection, resource wait behavior, annotation filtering, and stop timeout derivation.

## Important APIs, Types, And Functions
`validateLabels`, `mergeEnvs`, `getDecryptionKeys`, `getSourceMount`, `isContextError`, `(*Server).getResourceOrWait`, `(*Server).FilterDisallowedAnnotations`, and `stopTimeoutFromContext`. Constants define `maxLabelSize` and `defaultStopTimeout`.

## Control Flow
Label validation caps combined key/value length. Environment merging prioritizes kube-provided envs and appends image envs whose keys were not set by Kubernetes. Decryption key loading walks a directory, rejects symlinks, base64-encodes key files, sorts keys through ocicrypt, and initializes a decrypt config. Mount source lookup chooses the longest mountpoint prefix. Resource waiting first checks a cache, then waits on a resource watcher, context cancellation, or a defensive timeout, returning an error that asks kubelet to retry. Annotation filtering merges runtime-allowed and workload-allowed annotations before filtering.

## State And Persistence
Reads key files and mount metadata supplied by callers. `getResourceOrWait` observes server resourceStore state and emits a stalled-stage metric. `FilterDisallowedAnnotations` mutates `toFilter` by removing disallowed entries.

## Dependencies And Integration Points
Uses OCI image spec envs, CRI key/value types, ocicrypt config utilities, containers/storage mount info, CRI-O workload/runtime config, resourceStore, log tracing, and metrics.

## Risks And Test Signals
`getSourceMount` uses a raw string prefix, so mountpoint boundary handling depends on caller input. `stopTimeoutFromContext` can produce zero or negative seconds for expired deadlines. Resource waiting intentionally withholds a ready resource after waiting to avoid kubelet response leaks. Tests cover env merge, key loading, and mount source selection; other helpers rely on integration coverage.
