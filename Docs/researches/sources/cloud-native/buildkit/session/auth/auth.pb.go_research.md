<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.pb.go -->
# sources/cloud-native/buildkit/session/auth/auth.pb.go

Purpose: generated Go protobuf message definitions and descriptors for the Auth session service schema.

Important APIs, types, and functions: defines messages `CredentialsRequest`, `CredentialsResponse`, `FetchTokenRequest`, `FetchTokenResponse`, `GetTokenAuthorityRequest`, `GetTokenAuthorityResponse`, `VerifyTokenAuthorityRequest`, and `VerifyTokenAuthorityResponse`. Generated methods include `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated descriptors, getters for each field, raw descriptor compression, and file initialization.

Control flow and state: generated descriptor state is initialized once at package init. Message instances carry protobuf runtime state, size cache, unknown fields, and schema fields such as host, username, secret, realm, service, scopes, token, expiry, salt, payload, public key, and signed response.

Dependencies and integration: generated from `auth.proto` with `google.golang.org/protobuf` runtime. Used by handwritten auth helpers and authprovider server implementation.

Risks and test signals: this file should not be manually edited. Compatibility depends on preserving protobuf field numbers. Tests should target behavior through `auth.go`, `authprovider`, and wire round trips rather than generated internals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.pb.go -->
