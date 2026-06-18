# sources/cloud-native/buildkit/frontend/gateway/client/client_test.go

## Purpose

This file tests that `SolveRequest.Clone` correctly deep-copies frontend inputs and associated mutable fields.

## Important APIs, Types, And Functions

- `TestSolveRequestCloneCopiesFrontendInputs` constructs a solve request with frontend options and frontend input definitions, clones it, mutates the clone, and asserts the original is unchanged.

## Control Flow

The test builds a request containing a real `pb.Definition` and a nil input entry. It calls `Clone`, checks the cloned map retains both keys, asserts the non-nil definition pointer differs but is equal in value, mutates cloned frontend option and metadata, and verifies original data remains intact.

## State And Persistence Behavior

Only in-memory test state is used. The key persistence signal is negative: cloned state must not share mutable nested maps with the original request.

## Dependencies And Integration Points

It uses solver protobuf `pb.Definition`, `pb.OpMetadata`, and `testify/require`. It specifically protects the gateway client API used by forwarders and grpc clients when solve requests are reused or amended.

## Risks And Edge Cases

The test focuses on frontend inputs. Other fields in `Clone`, such as cache imports and source policies, rely on implementation review or separate coverage. If new mutable fields are added to `SolveRequest`, this test will not automatically detect missing clone logic unless extended.

## Test Signals

This is a strong regression signal for frontend input aliasing. It demonstrates that nil input definitions remain represented and that nested metadata maps are cloned through `CloneVT`.
