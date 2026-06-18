# sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils_test.go

## Purpose
This file tests conversion of internal `worker.WorkResult` records to BeeRemote protobuf job-result work-result records.

## Important APIs, Types, and Functions
`TestGetWorkResultsForResponse` builds two internal work results with distinct request IDs, nodes, pools, statuses, and messages, calls `getProtoWorkResults`, and verifies the response fields.

## Control Flow
The test uses the returned work result's request ID to reconstruct expected status/message/node values. This avoids assuming any ordering from Go map iteration.

## State and Persistence Behavior
The test is in-memory only and does not touch Badger or manager state. It verifies response construction over already materialized internal records.

## Dependencies and Integration Points
The test uses Testify, `worker.WorkResult`, `worker.BeeSync`, and `flex.Work` builders. It provides coverage for job-manager response helpers used by gRPC-facing APIs.

## Risks and Edge Cases
The test covers normal populated results but not nil `WorkResult`, empty maps, unknown pools, or duplicate/malformed request IDs. It also assumes request IDs are numeric for its expected-status calculation.

## Test Signals
Passing tests indicate that assigned node, assigned pool, status, and message survive conversion from internal state to protobuf response state.
