# sources/cloud-native/moby/client/service_list.go

## Purpose
Implements listing swarm services through the Docker API client with optional filters and service status reporting.

## APIs, Types, And Functions
`ServiceListOptions` exposes `Filters` and `Status`; `ServiceListResult` carries `[]swarm.Service`; `Client.ServiceList` performs the request. It depends on `Filters.updateURLValues`, `cli.get`, JSON decoding, and swarm API types.

## Control Flow, State, And Integration
The method builds query values from filters, adds `status=1` when requested, calls `GET /services`, decodes the response array, and closes the response reader. It has no persistence beyond the returned slice.

## Risks And Test Signals
Key risks are omitted filters, incorrect status query encoding, decode errors, and API type drift. The integration point is the daemon service-list endpoint used by swarm orchestration tools and CLI list commands.
