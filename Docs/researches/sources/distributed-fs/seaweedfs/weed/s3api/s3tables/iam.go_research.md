## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/iam.go

Purpose: bridges S3 Tables handlers to SeaweedFS IAM without importing the broader S3 API server package. It decides when to use IAM, builds IAM action requests, and extracts request identity details through reflection.

Important APIs: `IAMAuthorizer`, `SetIAMAuthorizer`, `shouldUseIAM`, `defaultAllowFor`, `authorizeIAMAction`, `extractSessionToken`, `getIdentityPrincipalArn`, `getIdentityPolicyNames`, `getIdentityClaims`, `buildIAMRequestContext`, and `getIdentityStructValue`.

Control flow: IAM is selected only when an authorizer and identity exist, except anonymous default-allow requests stay on the legacy fallback. Session tokens, missing inline actions, or named policies push evaluation through IAM. `authorizeIAMAction` normalizes action names to `s3tables:*`, resolves principal from headers or identity fields, forwards session token and policy names, and requires every non-empty resource to be allowed.

State and persistence: no persistent state; it reads request context, headers, query parameters, and handler configuration flags. Dependencies include `s3_constants`, IAM `integration.ActionRequest`, `glog`, and reflected identity structs.

Risks: reflection makes field-name drift easy to miss, missing principal/resource is a hard denial, and `defaultAllowFor` treats identity name without full identity as authenticated. Tests in `manager_test.go` cover default-allow/trusted manager distinctions; broader IAM policy paths need integration coverage.
