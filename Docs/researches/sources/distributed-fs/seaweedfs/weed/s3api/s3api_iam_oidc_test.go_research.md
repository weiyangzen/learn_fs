# sources/distributed-fs/seaweedfs/weed/s3api/s3api_iam_oidc_test.go

## Purpose
Tests the embedded IAM API's OpenID Connect provider actions against an in-memory IAM manager. It verifies provider listing, lookup, creation, mutation, deletion, read-only filtering, and persistence-like behavior through the configured IAM stores.

## Important APIs, Types, And Functions
`stubIntegration` supplies only `GetIAMManager`, deliberately panicking through embedded `IAMIntegration` for unexpected integration calls. `newOIDCTestAPI` creates an `integration.IAMManager` with STS OIDC providers for Google and GitHub, memory policy and role stores, and wires it into `EmbeddedIamApiForTest`. The tests exercise `ExecuteAction` with IAM query actions such as `ListOpenIDConnectProviders`, `GetOpenIDConnectProvider`, `CreateOpenIDConnectProvider`, `DeleteOpenIDConnectProvider`, `AddClientIDToOpenIDConnectProvider`, `RemoveClientIDFromOpenIDConnectProvider`, `UpdateOpenIDConnectProviderThumbprint`, `TagOpenIDConnectProvider`, and `UntagOpenIDConnectProvider`.

## Control Flow
Each test constructs IAM-style `url.Values`, calls `api.ExecuteAction(context, values, true, requestID)`, type-checks the returned response, and inspects response fields or IAM errors. Creation tests then fetch the created provider by ARN to confirm client IDs, thumbprints, and tags were stored. Mutation tests modify an existing static provider, fetch it, and verify idempotent add/remove behavior. Read-only tests set `api.readOnly` and confirm list is allowed while mutating OIDC actions are denied.

## State And Persistence
State is memory-backed but flows through the IAM manager and embedded API stores as production code would. Static provider configuration is initialized from `STSConfig.Providers`; dynamically-created providers and mutated client IDs, thumbprints, and tags are stored through the manager's configured in-memory stores.

## Dependencies And Integration Points
The tests integrate `weed/iam`, `weed/iam/integration`, STS provider configuration, policy engine defaults, embedded IAM API dispatch, and AWS-style IAM XML/query action response types. They indirectly validate ARN formatting using the configured account id `111122223333`.

## Risks And Test Signals
These tests signal regressions in action dispatch, read-only action classification, provider ARN parsing, duplicate conflict detection, required input validation, thumbprint format validation, tag round-tripping, and idempotency. Remaining risk is that they use memory stores and synthetic config, so external persistence backends, real OIDC discovery, and XML wire formatting are not covered here.
