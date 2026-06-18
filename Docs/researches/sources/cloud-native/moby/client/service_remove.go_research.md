# sources/cloud-native/moby/client/service_remove.go

## Purpose
Implements swarm service removal through the Docker API client.

## APIs, Types, And Functions
`ServiceRemoveOptions` is currently empty, `ServiceRemoveResult` is an empty result wrapper, and `Client.ServiceRemove` performs the operation. The method depends on `trimID` and `cli.delete`.

## Control Flow, State, And Integration
The method validates and normalizes the service ID, then sends `DELETE /services/{id}` without a request body or query parameters. No local client state is persisted; all state mutation occurs in the daemon's swarm service store.

## Risks And Test Signals
Risks are mostly API-contract mistakes: accepting empty IDs, wrong HTTP verb, or wrong path. Integration is direct with the daemon service delete endpoint, where successful calls delete swarm state and related task scheduling intent.
