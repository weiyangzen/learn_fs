# sources/distributed-fs/ceph/src/rgw/rgw_sts.cc

## Purpose
`rgw_sts.cc` implements Security Token Service request validation, assumed-role identity construction, encrypted temporary credential generation, role lookup, and GetSessionToken/AssumeRole/AssumeRoleWithWebIdentity flows.

## Important APIs, Types, and Functions
`Credentials::generateCredentials()` generates random access/secret keys, computes expiration, serializes `SessionToken`, encrypts it with AES using `rgw_sts_key`, and base64-encodes it. `AssumedRoleUser::generateAssumedRoleUser()` converts role ARN resources into assumed-role ARNs and role session ids. `AssumeRoleRequestBase::validate_input()` enforces duration, policy, ARN, and session-name constraints. Derived validators add provider id, external id, serial number, and token-code checks. `STSService::getRoleInfo()` parses ARNs and loads roles from SAL. `assumeRole()`, `assumeRoleWithWebIdentity()`, and `getSessionToken()` produce response structs.

## Control Flow
AssumeRole parses and loads the role, applies the role max session duration to the request, validates input, computes packed policy size, builds assumed-role user metadata, then generates credentials with policy and role id embedded in the token. Web identity mode builds token claims from issuer/audience/subject and principal tags, then generates role credentials. GetSessionToken skips role lookup and embeds the current identity fields.

## State and Persistence Behavior
The generated STS token is self-contained encrypted state carrying keys, expiration, policy, role id, user, account attributes, role session, token claims, issued-at time, and principal tags. The service stores a `unique_ptr` to the last loaded role while serving role operations. It does not persist new objects directly.

## Dependencies and Integration Points
The file integrates with RGW role SAL APIs, ARN parsing, IAM policy evaluation through embedded policy text, AES crypto handlers, `rgw_sts_key`, random generation, JSON formatting, Ceph time/ISO8601 helpers, account validation, and auth `Identity`.

## Risks
`MAX_DURATION_IN_SECS` is set through `setMaxDuration()` but is not initialized in the base constructor before validation unless callers set it. The token-code check rejects only non-empty six-character codes, which appears inverted for MFA-style validation. Packed policy size uses integer division before multiplying by 100, losing expected percentages below 100 percent. Web identity assumes `role` is already loaded and does not call `getRoleInfo()` in this file path.

## Test Signals
Cover missing/invalid `rgw_sts_key`, AES secret validation, duration min/max and role max duration, session-name regex, policy-size limits, malformed ARN/path mismatch, role-not-found mapping, web identity claim embedding, principal tags, encrypted token decode compatibility, and GetSessionToken identity propagation.
