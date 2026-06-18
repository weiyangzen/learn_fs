# sources/cloud-native/containerd/integration/image_pull_timeout_test.go

## Purpose

This Linux test suite validates CRI image pull progress timeout behavior for local pull and transfer-service paths. It distinguishes true network inactivity from benign waits such as slow content commit or singleflight waits on already-open content writers.

## Important APIs, Types, And Functions

- `TestCRIImagePullTimeout` runs six subtests across three scenarios and two pull implementations.
- `testCRIImagePullTimeoutBySlowCommitWriter` uses `tweakContentInitFnWithDelayer` to delay content commit.
- `testCRIImagePullTimeoutByHoldingContentOpenWriter` opens content writers for manifest descriptors to simulate singleflight waiters.
- `testCRIImagePullTimeoutByNoDataTransferred` uses a local mirror registry with a circuit-breaking copy limiter.
- `mirrorRegistryServer`, `ioCopyLimiter`, and `limitedCopy` implement the throttling HTTP proxy.
- `initLocalCRIImageService` constructs a CRI image service over a local containerd client.

## Control Flow

The suite runs only on Linux and in parallel. Slow-commit tests build a local containerd client with a delayed content store and expect pull success despite commit taking longer than the progress timeout. Holding-writer tests lock manifest descriptors, start a pull, ensure it does not return while blocked, release writers after multiple timeouts, and expect success. No-data-transferred tests configure a mirror that forwards to GHCR but sleeps after sending 3 MiB; CRI should cancel the pull with `context.Canceled` and the test cleans up the lease synchronously.

## State And Persistence Behavior

State is isolated in temporary containerd roots, content stores, leases, host registry config files, and httptest mirror state. `ioCopyLimiter.hitCircuitBreaker` records whether the simulated stall occurred.

## Dependencies And Integration Points

It integrates CRI image service internals, containerd content/lease APIs, registry mirror configuration, transfer service versus local pull behavior, HTTP auth header rewriting, and GHCR-hosted `volume-ownership:2.1`.

## Risks And Edge Cases

The tests depend on external network access to GHCR except for the local proxy layer. Parallel pulls can be resource-heavy. The mirror rewrites auth headers and assumes GHCR response shapes. Lease cleanup is required to remove failed pull content.

## Test Signals

Passing confirms CRI progress timeout cancels truly stalled network transfers but not commit delays or singleflight/content-lock waits.
