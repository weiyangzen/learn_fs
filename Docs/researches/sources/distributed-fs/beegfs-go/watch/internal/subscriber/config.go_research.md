# sources/distributed-fs/beegfs-go/watch/internal/subscriber/config.go

## Purpose

This file defines subscriber configuration and factory logic. It converts user-provided subscriber config into concrete `Subscriber` instances used by subscriber handlers.

## Important APIs, Types, And Functions

`Config` contains common subscriber fields `Type`, `ID`, `Name`, and embedded `GrpcConfig` squashed for Viper/mapstructure. `GrpcConfig` contains address, TLS certificate, TLS verification/disable flags, proxy flag, and disconnect timeout. `NewSubscribersFromConfig` creates all subscribers and fails on the first invalid config. `newSubscriberFromConfig` initializes common disconnected state and selects the implementation by `Type`.

## Control Flow

The current factory supports only `Type: "grpc"`. It wraps a `GRPCSubscriber` returned by `newGRPCSubscriber` inside a generic `Subscriber`. Unknown types return an error and prevent manager updates from applying.

## State And Persistence

The produced `Subscriber` holds static config, thread-safe state initialized to `DISCONNECTED`, and an implementation interface. No state is persisted here.

## Dependencies And Integration Points

It integrates with `subscribermgr.Manager.UpdateConfiguration`, which calls `NewSubscribersFromConfig` before adding/removing handlers. Mapstructure tags define the external TOML/env config contract.

## Risks And Test Signals

Subscriber IDs are not checked for duplicates here; duplicate IDs could confuse handler maps and ring-buffer cursors. Required fields such as gRPC address are not statically validated in this file. Tests confirm gRPC construction and default disconnect timeout, but more coverage is needed for unknown types, duplicate IDs, and missing addresses.
