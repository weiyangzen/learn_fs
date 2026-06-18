# sources/cloud-native/moby/integration-cli/daemon/daemon_swarm.go

## Purpose
Swarm-specific polling helpers for legacy integration tests.

## Important APIs and Types
Defines checks for service tasks in states/errors, running tasks, service update state, plugin running/image state, task networks/images, node ready count, local node state, control availability, leader detection, and `CmdRetryOutOfSequence`.

## Control Flow, State, and Persistence
Each method returns a polling closure that runs Docker CLI commands against the daemon, parses JSON/text output, and returns poll success/continue/error. `CmdRetryOutOfSequence` retries commands that fail due to Raft out-of-sequence errors.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on swarm API CLI output, poll helpers, and daemon command wrapper. Risks include fragile output parsing, races during convergence, and masking real errors as retryable. Swarm integration suite tests validate these helpers.
