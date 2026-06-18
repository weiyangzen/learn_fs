# sources/cloud-native/containerd/core/images/handlers.go

## Purpose

This file defines the descriptor traversal and handler composition framework used throughout image fetch, walk, filtering, labeling, and referrer traversal. It provides both synchronous and parallel recursion over OCI descriptors.

## Important APIs, Types, and Functions

`Handler` and `HandlerFunc` define descriptor processors. `Handlers` chains handlers and honors `ErrStopHandler`. `Walk` recursively visits descriptors synchronously and honors `ErrSkipDesc`. `WalkNotEmpty` wraps `Walk` and returns `ErrEmptyWalk` when traversal yields no children. `Dispatch` recursively visits siblings in parallel with optional `semaphore.Weighted` concurrency limiting. `ChildrenHandler` adapts `Children`. `SetReferrers`, `SetChildrenLabels`, and `SetChildrenMappedLabels` enrich child lists or content labels. `FilterPlatforms` and `LimitManifests` filter and order descriptor children by platform.

## Control Flow

`Handlers` calls each handler for a descriptor and appends all children unless a handler returns `ErrStopHandler`. `Walk` processes each descriptor, recurses into returned children, and treats `ErrSkipDesc` as pruning. `Dispatch` starts one errgroup goroutine per sibling, acquires/releases the limiter around each handler invocation, cancels the group context on errors, and recurses on children. The label wrappers execute an underlying child-returning handler first, then update parent content metadata with generated GC reference labels before returning children.

## State and Persistence Behavior

Most handlers are stateless. `SetChildrenMappedLabels` mutates content metadata by writing label fields onto the parent descriptor's content info. Labels encode child digests using keys from `ChildGCLabels` or caller-provided mappings, add numeric suffixes for repeated key classes, and use digest hex suffixes for referrer SHA256 keys. `SetReferrers` mutates returned referrer descriptors in memory by adding `AnnotationManifestSubject`.

## Dependencies and Integration Points

The traversal APIs integrate with `core/content` providers/managers, OCI descriptors, platform matchers/comparers, `errgroup`, semaphores, and containerd media-type helpers. Fetchers, unpackers, GC label creation, manifest platform resolution, and referrer-aware operations compose these handlers.

## Risks and Edge Cases

`Dispatch` starts goroutines inside a loop with a local `desc := desc` inside the goroutine, which is safe on modern Go but still worth preserving if edited. Limiter acquisition happens before goroutine start and release after handler return; handler panics would leak semaphore capacity. `SetChildrenMappedLabels` assumes label keys are non-empty before indexing `key[len(key)-1]`. `LimitManifests` only errors on no match when a positive limit is requested. Platform-less descriptors are retained by filtering and sorted after platform-matched descriptors.

## Test Signals

Tests should exercise handler-chain stopping, skip-desc pruning, WalkNotEmpty empty detection, Dispatch error cancellation and limiter behavior, referrer annotation injection, GC label key generation including repeated keys and referrers, platform filtering, manifest limiting, and not-found behavior when no platform match exists.
