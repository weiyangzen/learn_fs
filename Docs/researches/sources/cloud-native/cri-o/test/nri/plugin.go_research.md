# sources/cloud-native/cri-o/test/nri/plugin.go

## Purpose
In-process NRI test plugin used by integration tests to observe events and inject container adjustments/updates.

## Important APIs, Types, And Functions
Defines `PluginOption`, `plugin`, `event`, option constructors (`WithStubOptions`, `WithTestNamespace`, `WithCreateHandler`, `WithPostCreateHandler`, `WithStopHandler`, `WithUpdateHandler`), `NewPlugin`, lifecycle methods `Start`/`Stop`, NRI callbacks, event pump/read helpers, event matching, and event factory functions.

## Control Flow
`Start` builds a containerd NRI stub with plugin name/index/socket and close callback, starts an event pump goroutine, then starts the stub. NRI callbacks filter by namespace, update in-memory pod/container maps, call optional handler hooks, emit events, and return requested adjustments or updates. `pumpEvents` buffers writes from callbacks to avoid blocking readers. Tests poll, wait, or verify ordered streams against expected event descriptors.

## State And Persistence
Maintains in-memory maps of synchronized/running pods and containers, channels for event write/read, a done channel, and a `sync.Once` stop guard. No persistent files.

## Dependencies And Integration Points
Implements containerd NRI stub callback surface and is driven by CRI-O's NRI socket. Used directly by `nri_suite_test.go` and `nri_test.go`.

## Risks And Test Signals
`Configure` returns event mask 0, relying on default/full callback behavior from the stub/runtime. `VerifyEventStream` ignores its `exact` argument and only waits for ordered expected matches, so extra events can pass. Event emission can block if `pumpEvents` has stopped while callbacks continue. It provides the core signal for NRI event ordering, namespace filtering, and adjustment propagation.
