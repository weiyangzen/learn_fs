<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/health.go -->
# sources/cloud-native/cri-o/server/health.go

## Purpose

This file implements CRI-O health checking through a self-CRI status call and asynchronous CNI readiness gating.

## Important APIs, Types, and Functions

`checkCRIHealth(ctx, timeout)` creates a remote runtime client to CRI-O's own socket, calls `Status`, validates runtime conditions, and handles NetworkReady specially. `cniPluginReadinessCheck(ctx)` starts a one-time goroutine that waits for CNI readiness and flips the package-level atomic `cniPluginInitialized`.

## Control Flow

The health check opens a remote runtime service, defers close, requests runtime status, rejects nil status or nil conditions, starts the CNI readiness check, then iterates conditions. A false `NetworkReady` condition is ignored until CNI has been initialized at least once; other false conditions return an error with message and reason.

## State and Persistence Behavior

State is process-global: `cniPluginInitialized` and `cniInitOnce`. No disk state is written. The readiness goroutine logs success or failure and stores readiness in the atomic flag.

## Dependencies and Integration Points

It depends on `k8s.io/cri-client`, server listen socket config, runtime status conditions, CNI plugin readiness via `waitForCNIPlugin`, and logging.

## Risks and Edge Cases

Global once/atomic state means readiness is process-wide, not per server instance. If the first readiness goroutine fails, `cniInitOnce` prevents retry through this path, leaving NetworkReady ignored only while the atomic remains false but without another checker starting. Health depends on CRI-O being able to connect to its own socket.

## Test Signals

No tests are included in this subset. Useful coverage would mock remote status conditions and CNI readiness transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/health.go -->
