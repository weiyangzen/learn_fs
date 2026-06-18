# sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype_test.go

## Purpose
Tests strict Accept matching and general content negotiation behavior.

## Important APIs, Types, And Functions
`TestMatchAcceptStrict` table-tests `contenttype.MatchAcceptStrict`. `TestNegotiateContentType` ports Go/gddo negotiation cases for `contenttype.Negotiate`.

## Control Flow
Each strict test constructs headers, calls the helper, and compares the expected media type. Negotiation tests iterate Accept strings, offers, defaults, and expected results.

## State And Persistence
No external state. Some strict tests run in parallel with local header maps.

## Dependencies And Integration Points
Depends on Go `net/http`, the local contenttype package, and standard testing. It guards container log format negotiation.

## Risks And Edge Cases
The tests explicitly distinguish strict matching from wildcard negotiation, preventing future accidental JSON log opt-in through broad Accept headers.

## Test Signals
Failures indicate changed q-value ordering, wildcard treatment, exact-match requirements, or fallback negotiation semantics.
