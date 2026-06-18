<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.proto -->
# sources/cloud-native/buildkit/session/auth/auth.proto

Purpose: protobuf contract for BuildKit session registry authentication.

Important APIs, types, and functions: package `moby.filesync.v1` with Go package `github.com/moby/buildkit/session/auth`. Service `Auth` exposes unary RPCs `Credentials`, `FetchToken`, `GetTokenAuthority`, and `VerifyTokenAuthority`. Messages carry host credentials, token request realm/service/scopes, token response token/expiry/issued-at, token authority salt/public key, and challenge payload/signed response.

Control flow and state: schema only. State is carried in RPC messages and handled by generated code plus authprovider implementation.

Dependencies and integration: consumed by generated Go, vtprotobuf, and gRPC stubs. Registry pull code and session auth providers use this service across BuildKit sessions.

Risks and test signals: the declared proto package name says `moby.filesync.v1`, which is unusual for auth and must remain compatible if clients depend on it. Field-number changes would break wire compatibility. Test by regenerating stubs and running auth provider tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.proto -->
