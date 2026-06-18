# sources/cloud-native/moby/client/task_inspect_test.go

## Purpose
Tests swarm task inspection for daemon errors, empty IDs, and successful JSON decoding.

## APIs, Types, And Functions
The tests are `TestTaskInspectError`, `TestTaskInspectWithEmptyID`, and `TestTaskInspect`. They use `Client.TaskInspect`, `TaskInspectOptions`, mock `GET /tasks/task_id`, `swarm.Task`, and errdefs assertions.

## Control Flow, State, And Integration
The empty-ID test checks local validation. Other tests assert request method/path and return either a server failure or a JSON task with an ID to decode.

## Risks And Test Signals
Signals protect endpoint and validation behavior. Coverage is intentionally narrow and does not exhaustively check all task fields.
