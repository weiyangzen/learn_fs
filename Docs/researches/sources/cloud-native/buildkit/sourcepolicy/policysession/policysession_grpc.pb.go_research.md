# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_grpc.pb.go

## Purpose
Generated Go protobuf definitions for the policy-session RPC contract. It defines CheckPolicyRequest, CheckPolicyResponse oneof wrappers, DecisionResponse, and DenyMessage plus descriptors/getters.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `_, PolicyVerifierClient, policyVerifierClient, NewPolicyVerifierClient, CheckPolicy, PolicyVerifierServer, UnimplementedPolicyVerifierServer, testEmbeddedByValue, UnsafePolicyVerifierServer, RegisterPolicyVerifierServer, _PolicyVerifier_CheckPolicy_Handler, PolicyVerifier_ServiceDesc`.

## Control Flow, State, And Persistence
Control flow is protobuf runtime reflection and accessor code generated from policysession.proto. It stores request/response fields in memory only and integrates with frontend gateway, solver SourceOp, and sourcepolicy PolicyAction types.

## Dependencies And Integration Points
Important dependencies/imports: `google.golang.org/grpc, google.golang.org/grpc/codes, google.golang.org/grpc/status`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are schema compatibility and oneof handling across clients. Runtime behavior is tested indirectly through provider/verifier integration.
