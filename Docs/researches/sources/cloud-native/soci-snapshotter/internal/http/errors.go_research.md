# sources/cloud-native/soci-snapshotter/internal/http/errors.go

Purpose: shared sentinel errors for the internal auth HTTP client.

Important APIs/types/functions: declares `ErrMissingAuthHandler`, `ErrFailedToAuthorizeRequest`, and `ErrFailedToHandleChallenge`.

Control flow: no standalone flow; `AuthClient.Do` wraps lower-level handler failures with these sentinels so callers can classify auth setup, authorization, and challenge-handling failures.

State and persistence: immutable package-level error values.

Dependencies/integration points: used by `auth.go` and any callers that check errors with `errors.Is`.

Risks: wrapped errors must preserve these sentinels with `%w`; current auth client does that for authorize/challenge failures.

Test signals: indirectly exercised by auth tests; no dedicated `errors.Is` assertions.
