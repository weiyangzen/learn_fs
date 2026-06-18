# sources/distributed-fs/beegfs-go/watch/internal/subscriber/config_test.go

## Purpose

This file tests subscriber factory behavior for configured gRPC subscribers and the comparable-test helpers used to compare structs with non-comparable fields.

## Important APIs, Types, And Functions

`testConfig` defines two gRPC subscribers. `TestNewSubscribersFromConfig` calls `NewSubscribersFromConfig`, builds expected `Subscriber` and `GRPCSubscriber` objects, then compares common fields through `newComparableSubscriber`.

## Control Flow

The test validates slice length, common subscriber config/state, and implementation-specific gRPC config. It also switches over the concrete `Interface` type to make adding new subscriber types a deliberate test update.

## State And Persistence

All state is in memory. It specifically verifies initial state is `DISCONNECTED` and that `DisconnectTimeout` defaults to 30 when unset.

## Dependencies And Integration Points

It depends on testify assertions and `subscriber` package test helper `ComparableGRPCSubscriber`. It protects the configuration contract used by `subscribermgr.Manager.UpdateConfiguration`.

## Risks And Test Signals

The test is good at catching factory output drift, but it does not test error paths for unknown subscriber type, malformed config, or duplicate subscriber ID. It also does not verify TLS/proxy behavior because connection establishment is covered by runtime integration rather than unit tests.
