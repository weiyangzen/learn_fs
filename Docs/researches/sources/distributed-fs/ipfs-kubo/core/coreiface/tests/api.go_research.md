# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/api.go

## Purpose
Defines the shared CoreAPI conformance test harness.

## Important APIs, Types, and Functions
Declares `Provider`, `TestSuite`, helper methods `makeAPISwarm`, `makeAPI`, `makeAPIWithIdentityAndOffline`, `MakeAPISwarm`, `hasApi`, and `TestApi`.

## Control Flow and State
Providers create swarms with requested identity/online settings. `TestApi` runs subtests for every CoreAPI domain, tracks live API swarms through a channel, cancels contexts, and verifies all spawned swarms terminate by the final `TestsCancelCtx` subtest.

## Dependencies and Integration Points
Depends on testing, context, and the CoreAPI interface. Implementations plug in by providing `MakeAPISwarm`.

## Risks and Test Signals
Risks include shared running counter races, providers ignoring full-identity/offline flags, and test contexts leaking resources. The final cleanup subtest is the main signal for context cancellation discipline.
