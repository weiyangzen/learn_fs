# sources/cloud-native/moby/daemon/server/middleware/version.go

## Purpose
Validates requested Docker API versions, sets standard version/OS response headers, and stores the effective API version in request context.

## Important APIs, Types, And Functions
`VersionMiddleware`, `NewVersionMiddleware`, `versionUnsupportedError`, and `WrapHandler` are the core APIs. `versionUnsupportedError` implements `InvalidParameter`.

## Control Flow
Construction validates default and minimum API versions are within daemon-supported bounds and that minimum is not above default. The wrapper sets `Server`, `Api-Version`, and `Ostype` headers, defaults missing route version to the server default, rejects versions below minimum or above default, stores the effective version in context under `httputils.APIVersionKey`, and calls the handler.

## State And Persistence
No persistent state changes. The middleware writes headers and creates a derived context for downstream handlers.

## Dependencies And Integration Points
Uses daemon config version constants, version comparison helpers, Go runtime OS, and httputils context key. API routers consume `VersionFromContext` for compatibility behavior.

## Risks And Edge Cases
Version comparisons are string-based through helper functions and rely on normalized `major.minor` inputs. Error responses still include version headers because headers are set before validation.

## Test Signals
`version_test.go` covers constructor validation, context version defaults/requested values, too-old/too-new errors, and headers on error.
