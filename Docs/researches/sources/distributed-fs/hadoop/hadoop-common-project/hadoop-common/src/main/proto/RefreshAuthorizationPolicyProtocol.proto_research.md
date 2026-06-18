# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshAuthorizationPolicyProtocol.proto

## Purpose
`RefreshAuthorizationPolicyProtocol.proto` defines the protobuf RPC used to ask a Hadoop daemon to reload service authorization policy.

## Important APIs, types, and functions
The schema has empty request/response messages `RefreshServiceAclRequestProto` and `RefreshServiceAclResponseProto`. `RefreshAuthorizationPolicyProtocolService` exposes `refreshServiceAcl`.

## Control flow
An admin client sends the empty request; the server reloads authorization policy from configuration and returns an empty response or an RPC exception on failure. Generated service stubs handle transport.

## State and persistence
The proto carries no payload. The state change is external: server-side in-memory authorization policy is refreshed from configured sources.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.RefreshAuthorizationPolicyProtocolProtos` and integrates with Hadoop service ACL refresh commands and server-side authorization managers.

## Risks and test signals
Risks include unauthorized callers triggering policy reloads, empty responses hiding partial reload failures, and compatibility around service naming. Test signals include admin CLI tests, authorization enforcement before/after refresh, failure-to-read-config behavior, and RPC authorization tests.
