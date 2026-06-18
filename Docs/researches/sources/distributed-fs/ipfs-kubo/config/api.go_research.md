# Research: sources/distributed-fs/ipfs-kubo/config/api.go

Purpose: Defines RPC API HTTP header and authorization configuration plus helper conversion for stored auth secrets.

Important APIs/types/functions: Constants `APITag` and `AuthorizationTag`; `RPCAuthScope` with `AuthSecret` and `AllowedPaths`; `API` with `HTTPHeaders` and `Authorizations`; `ConvertAuthSecret(secret)`.

Control flow, state, and persistence: `ConvertAuthSecret` treats no-prefix secrets as bearer tokens, supports `bearer:<token>`, supports `basic:user:pass` by base64-encoding the user/password portion, and passes through `basic:<base64>` values. Unknown typed prefixes return an empty string. Secrets are persisted in repo config if configured.

Dependencies and integration points: Used by HTTP RPC server auth setup. Depends on `encoding/base64` and `strings`.

Risks and test signals: Unknown prefix returning `""` can turn configuration mistakes into failed auth matching; callers must handle empty converted values safely. Basic pre-encoded detection is heuristic: absence of a colon means "already base64". `api_test.go` covers the documented conversions.
