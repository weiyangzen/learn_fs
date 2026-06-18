# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3AccessProvider.java

## Purpose
`KeystoneV3AccessProvider` authenticates a Swift/JOSS account against Keystone v3 using password credentials.

## Important APIs, Types, And Functions
It implements JOSS `AccessProvider`. `authenticate` builds Keystone JSON request objects, posts to `AccountConfig.getAuthUrl`, expects HTTP 201, reads `X-Subject-Token`, parses the service catalog, and returns `KeystoneV3Access`. Nested request/response classes map Jackson JSON fields.

## Control Flow
Authentication constructs a password-scope request using username, password, and tenant/project id. It sends JSON via Apache HTTP client, rejects non-201 responses, parses the first response-body line, scans catalog entries named `swift` with type `object-store`, selects endpoints matching preferred region, and captures public/internal URLs.

## State And Persistence
The provider stores only `AccountConfig`. Tokens and endpoints are returned in an access object and are not persisted.

## Dependencies And Integration Points
It depends on JOSS, Apache HttpClient, Jackson, and Keystone response schema. Swift UFS account creation can use it for v3 auth.

## Risks
It returns null on many failures instead of throwing, which can defer errors. It reads only one response line and assumes headers/catalog fields exist. Endpoint selection is region-exact and may return access with null URLs.

## Test Signals
No direct test is listed in this subset, so behavior is mainly protected by compilation and any higher-level Swift authentication tests.
