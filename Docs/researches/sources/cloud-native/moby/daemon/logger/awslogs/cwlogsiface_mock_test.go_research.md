## sources/cloud-native/moby/daemon/logger/awslogs/cwlogsiface_mock_test.go

Purpose: Test doubles for the `awslogs` driver, including a mock CloudWatch Logs API client and mock IMDS region client.

Important APIs and types: `mockClient` has function fields for `CreateLogGroup`, `CreateLogStream`, and `PutLogEvents`. Its methods delegate to those fields, while `PutLogEvents` first calls `checkPutLogEventsConstraints`. `checkPutLogEventsConstraints` enforces maximum bytes per event and maximum bytes per put. `mockmetadataclient`, `regionResult`, `newMockMetadataClient`, and `GetRegion` simulate IMDS region lookup through a buffered channel.

Control flow and state: Tests configure function fields per scenario. Constraint checking makes mocked `PutLogEvents` fail when implementation batching violates CloudWatch size rules, raising test fidelity beyond a simple stub.

Dependencies and integration points: Mirrors the production `api` and `regionFinder` interfaces from `cloudwatchlogs.go` and uses AWS SDK input/output types.

Risks covered: Helps catch regressions in event splitting and batch size accounting even when tests do not hit real AWS. Function fields must be set before use; missing fields would panic.

Test signals: Supports most of the awslogs test suite and provides deterministic API behavior.
