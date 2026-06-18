<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.go -->
# sources/cloud-native/buildkit/session/secrets/secrets.go

Purpose: client helper for retrieving secret bytes from a BuildKit session.

Important APIs, types, and functions: `SecretStore` interface defines `GetSecret(context.Context, string)`. `ErrNotFound` is a package sentinel. `GetSecret(ctx, c, id)` derives caller context, creates a `SecretsClient`, calls `GetSecret`, maps unimplemented and not-found gRPC codes to wrapped `ErrNotFound`, and returns response data.

Control flow and state: no persistence. Each call is a unary session RPC.

Dependencies and integration: generated secrets gRPC client, session caller, BuildKit gRPC code helper, and secretsprovider server.

Risks and test signals: unimplemented is treated as not found for backward compatibility, which can hide client/server version mismatches. Tests should cover successful retrieval, not found mapping, unimplemented mapping, and other errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.go -->
