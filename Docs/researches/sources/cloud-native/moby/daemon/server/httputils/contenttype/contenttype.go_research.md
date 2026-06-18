# sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype.go

## Purpose
Provides content negotiation helpers for Docker API handlers, including strict explicit Accept matching and general negotiation.

## Important APIs, Types, And Functions
`MatchAcceptStrict(requestHeaders, offers)` returns the best exact media-type match from the Accept header, ignoring wildcards and q=0. `Negotiate(requestHeaders, offers, defaultOffer)` delegates to `httputil.NegotiateContentType`.

## Control Flow
Strict matching parses Accept specs, iterates offers first, then specs, keeps the match with the highest q value, and preserves offer order on ties. General negotiation builds a synthetic request and delegates to the upstream utility.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by container logs to opt into JSON streaming only when clients explicitly ask for supported JSON stream media types. Depends on `github.com/golang/gddo/httputil/header`.

## Risks And Edge Cases
Strict matching intentionally ignores `*/*` and `type/*`, which differs from normal HTTP negotiation but prevents accidental opt-in to experimental stream formats.

## Test Signals
`contenttype_test.go` covers no header, wildcards, q=0, q ordering, duplicate media types, and general negotiation cases.
