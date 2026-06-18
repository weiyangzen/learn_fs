# sources/cloud-native/moby/client/system_info.go

## Purpose
Implements retrieval of daemon system information.

## APIs, Types, And Functions
`InfoOptions` is currently empty; `SystemInfoResult` embeds `system.Info`; `Client.Info` sends the request and decodes the result.

## Control Flow, State, And Integration
The method creates an empty query, calls `GET /info`, decodes JSON into `system.Info`, and closes the response body. It reads daemon runtime state including drivers, resources, plugins, security options, and discovered devices.

## Risks And Test Signals
Risks are schema drift, invalid JSON handling, and callers depending on optional fields. Integration is broad because `/info` feeds diagnostics, CLI display, and capability detection.
