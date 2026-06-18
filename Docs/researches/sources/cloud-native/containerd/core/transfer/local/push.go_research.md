# sources/cloud-native/containerd/core/transfer/local/push.go

## Purpose
This file implements local image push from an image store source to a remote pusher, with optional upload progress.

## Important APIs, Types, and Functions
`localTransferService.push` drives image lookup and `remotes.PushContent`. `progressPusher` wraps a remote pusher and tracks upload status. `pushStatus` implements active status and content check. `progressWriter` updates offsets and marks completion.

## Control Flow
Push chooses a platform matcher from `ImagePlatformsGetter`, gets the image, creates a remote pusher, optionally wraps it with a progress tracker, and calls `remotes.PushContent` with upload limiter and handler wrapper. The wrapper adds descriptors and child relationships to progress. Writer commits mark content complete and handle already-exists progress.

## State and Persistence
The method reads local image/content and writes to the remote registry. In-memory maps track active refs and completed digests for progress.

## Dependencies and Integration Points
Uses transfer image getter/pusher interfaces, `remotes.PushContent`, `content.Ingester`, platform matchers, semaphore limiter, and local progress tracking.

## Risks
Progress status must remain consistent across already-existing pushes, commit failures, and content writers opened through either `content.Ingester` or remote `Pusher`. Push is sensitive to platform matcher configuration.

## Test Signals
Indirect coverage comes from push integration paths; no direct unit test in this subset.
