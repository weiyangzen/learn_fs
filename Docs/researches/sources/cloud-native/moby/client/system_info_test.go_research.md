# sources/cloud-native/moby/client/system_info_test.go

## Purpose
Tests system info error handling, invalid JSON handling, basic decode behavior, and discovered-device fields.

## APIs, Types, And Functions
The tests include `TestInfoServerError`, `TestInfoInvalidResponseJSONError`, `TestInfo`, and `TestInfoWithDiscoveredDevices`. They exercise `Client.Info`, `InfoOptions`, and `system.Info`.

## Control Flow, State, And Integration
Mock handlers validate `GET /info`, return server failures, malformed JSON, or structured info responses. The tests assert expected errors and decoded fields, including newer discovered-device data.

## Risks And Test Signals
Signals cover response decode robustness and schema additions. Since `/info` is a large structure, tests sample important fields rather than exhaustively verifying every daemon capability.
