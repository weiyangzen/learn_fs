# sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver_test.go

Purpose: targeted tests for action resolver passthrough and precedence rules.

Important APIs and functions: `TestMapBaseActionToS3Format_ServicePrefixPassthrough` validates `s3:`, `iam:`, and `sts:` actions are preserved and legacy `Read`/`Write` map to object actions. `TestResolveS3Action_STSActionsPassthrough` verifies STS actions survive through `ResolveS3Action` with and without HTTP context. `TestResolveS3Action_AttributesBeforeVersionId` checks that `?attributes&versionId=` resolves to `s3:GetObjectAttributes`, while plain versionId resolves to object-version actions.

Control flow: tests construct minimal requests and compare resolved action strings.

State and persistence: no state.

Dependencies and integration: directly validates `s3_action_resolver.go` and `s3_constants`.

Risks: the test file is focused and does not cover the full subresource table; broader coverage lives in `s3_granular_action_security_test.go`.

Test signals: strong signal for mixed IAM/STS integration and a subtle query precedence bug class.
