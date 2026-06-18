# sources/cloud-native/moby/client/service_inspect.go

## Purpose
Implements service inspection for the Docker API client, returning a typed swarm service plus raw response metadata for a single service identifier.

## APIs, Types, And Functions
`ServiceInspectOptions` carries `InsertDefaults`; `ServiceInspectResult` wraps `swarm.Service` and raw JSON bytes; `Client.ServiceInspect` is the public method. It depends on `trimID`, `cli.get`, `ensureReaderClosed`, JSON decoding, and `swarm.Service`.

## Control Flow, State, And Integration
The method validates and trims the service ID, conditionally sets `insertDefaults=1`, sends `GET /services/{id}`, reads the entire response into the result body, then unmarshals it into the service value. It persists no client state and uses request query parameters as the only mutation surface.

## Risks And Test Signals
Risk centers on empty or malformed IDs, response-body lifetime, and preserving raw JSON for callers that need fields beyond the typed struct. Integration points are the daemon service inspect endpoint, API query encoding, and swarm type evolution.
