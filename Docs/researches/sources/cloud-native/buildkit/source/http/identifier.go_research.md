# sources/cloud-native/buildkit/source/http/identifier.go

## Purpose
Defines the identifier model for BuildKit HTTP/HTTPS sources and their provenance capture behavior.

## Important APIs, Types, And Functions
- `NewHTTPIdentifier(str, tls)` prefixes `http://` or `https://` around the source ref.
- `HTTPIdentifier` stores URL, TLS mode, optional checksum, output filename, mode/owner, auth secret, allowed headers, and PGP signature verification options.
- `HTTPSignatureVerifyOptions` carries armored public key and detached signature bytes.
- `HeaderField` stores user-defined headers.
- `Scheme` returns `http` or `https`.
- `Capture` parses the pin digest and records an HTTP provenance source.

## Control Flow
`source/http.Source.Identifier` constructs this type, then applies attrs. During solve, `Source.Resolve` requires this concrete identifier and passes it to `httpSourceHandler`.

## State And Persistence
No persistence in this file. It is a value object copied into handler state.

## Dependencies And Integration Points
Uses BuildKit provenance capture, `source.Identifier`, source type constants, OCI digest parsing, and errors. It integrates with `source.Manager` via `Scheme`.

## Risks And Edge Cases
`NewHTTPIdentifier` unconditionally prepends the protocol to the `ref` portion supplied by `source.Manager`; callers must pass the post-scheme ref. `Capture` fails if the solver pin is not a valid digest.

## Test Signals
HTTP source tests indirectly validate pins, cache keys, and default naming; provenance capture is not deeply tested in the assigned files.
