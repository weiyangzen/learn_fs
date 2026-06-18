# sources/distributed-fs/seaweedfs/weed/s3api/s3api_inline_policy_condition_test.go

## Purpose
Regression tests inline IAM policy condition enforcement for S3 authorization, especially `aws:SourceIp` conditions on user and group inline policies. The file exists to prevent inline policies from being flattened into legacy action lists that lose condition blocks.

## Important APIs, Types, And Functions
`inlineCondPolicyDoc(cidr)` builds an S3 allow policy on `inline-cond-bucket` with an `IpAddress` condition. `inlineCondRequest` creates a synthetic HTTP request with `RemoteAddr` set to loopback. `seedInlineCondUser` adds user `alice` and a credential to `api.mockConfig`, saves it through the credential manager, reloads IAM, and returns the loaded identity. Tests call `PutUserPolicy`, `PutGroupPolicy`, `ListGroupPolicies`, `GetGroupPolicy`, `DeleteGroupPolicy`, `credentialManager.PutUserInlinePolicy`, `refreshIAMConfiguration`, and `VerifyActionPermission`.

## Control Flow
The user-policy tests install a nonmatching CIDR and expect `ErrAccessDenied`, then install a matching loopback CIDR and expect `ErrNone`. A discriminator test replaces a matching policy with a nonmatching one for the same user and action to prove the condition, not the legacy action list, controls the decision. The group test creates group `devs`, adds `alice`, puts a group inline policy, verifies deny and allow after CIDR replacement, confirms list/get round-trip includes the condition block, deletes the policy, and confirms access is revoked. The reload test writes a parsed `policy_engine.PolicyDocument` directly to the credential manager and reloads IAM to simulate process restart.

## State And Persistence
State is stored in the embedded test credential manager and in-memory IAM indexes. The tests exercise reload boundaries so persisted inline policies must be re-registered into the policy engine after `LoadS3ApiConfigurationFromCredentialManager`.

## Dependencies And Integration Points
The file integrates the embedded IAM test API, protobuf S3 configuration, policy-engine parsing, S3 action constants, S3 error constants, group credential APIs, HTTP request source-IP extraction, and identity authorization.

## Risks And Test Signals
Strong signals include condition-aware allow/deny decisions, group inline policy implementation, list/get/delete round-trips, and reload behavior. Risks not covered include other condition keys, IPv6, forwarded source headers, managed policies, concurrent IAM updates, and non-memory stores.
