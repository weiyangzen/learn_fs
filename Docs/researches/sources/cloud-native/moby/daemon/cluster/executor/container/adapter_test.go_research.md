# sources/cloud-native/moby/daemon/cluster/executor/container/adapter_test.go

## Purpose
Tests that `containerAdapter.waitNodeAttachments` blocks until required overlay network node attachments are present while ignoring non-overlay networks.

## Important APIs, Types, And Functions
Defines `TestWaitNodeAttachment`, using a bare `daemon.Daemon`, its attachment store, a hand-built `containerConfig`, and `containerAdapter.waitNodeAttachments`.

## Control Flow
The test seeds one overlay attachment, starts `waitNodeAttachments` in a goroutine for two overlay networks and one bridge network, verifies it does not finish early, then adds the second overlay attachment and verifies the wait completes without error.

## State And Persistence
State is in the daemon attachment store and goroutine-local variables. No persistent filesystem state.

## Dependencies And Integration Points
Directly covers adapter behavior that coordinates swarm overlay network readiness with daemon attachment state.

## Risks And Test Signals
The test relies on sleeps around the 100 ms polling interval, so very slow environments could be flaky. It currently uses `t.Context()` and does not explicitly cancel before normal completion.
