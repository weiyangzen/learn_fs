# sources/distributed-fs/ceph/src/rgw/rgw_sts.h

## Purpose
`rgw_sts.h` declares RGW's STS request, response, token, credential, and service types.

## Important APIs, Types, and Functions
`AssumeRoleRequestBase` owns duration, policy, role ARN, role session name, and shared validation limits. `AssumeRoleWithWebIdentityRequest`, `AssumeRoleRequest`, and `GetSessionTokenRequest` represent STS operation inputs. `AssumedRoleUser` exposes assumed-role ARN/id output. `SessionToken` is the encoded authorization payload, versioned through struct version 5. `Credentials` stores access key, secret key, session token, and expiration. `STSService` coordinates role loading and STS operations.

## Control Flow
Construct request objects from REST parameters, call `validate_input()`, then feed validated requests into `STSService`. The service returns simple structs/tuples with negative RGW/Ceph error codes or populated credentials.

## State and Persistence Behavior
`SessionToken` is a persisted wire/storage format inside encrypted session tokens; decoding preserves backward compatibility for role session, token claims, issued-at, and principal tags by checking struct version. Other classes are transient request/response containers.

## Dependencies and Integration Points
The header depends on `rgw_role.h`, `rgw_auth.h`, `rgw_web_idp.h`, Ceph encoding macros, SAL driver/role types, `rgw_user`, and auth identity. It is used by STS REST handlers and auth code that decrypts session tokens.

## Risks
Public getters expose references to mutable internals, so callers must respect object lifetime. Constructor parsing of GetSessionToken uses `stoull()` and can throw, unlike the base request's strict parser. Type aliases repeat struct names, which is harmless but noisy.

## Test Signals
Test binary encode/decode compatibility across `SessionToken` versions, construction from empty and numeric durations, role/session getters, response formatting, and service integration with mocked SAL roles and identities.
