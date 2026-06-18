# sources/distributed-fs/beegfs-go/ctl/internal/util/url.go

Purpose: builds a deterministic URL query string with an HMAC-SHA256 signature over its encoded parameters.

Important APIs/types/functions: `URLEncodeSignMap`.

Control flow: adds all map entries to `url.Values`, encodes them, signs the encoded string with the value stored at `m[key]`, base64url-encodes the MAC without padding, appends it as `mac`, and returns the final encoded query.

State and persistence: stateless.

Dependencies and integration points: uses standard `net/url`, `crypto/hmac`, `crypto/sha256`, and base64 raw URL encoding. Used where CTL needs signed GET-style argument strings.

Risks: if `key` is absent, the HMAC key is the empty string because `m[key]` returns zero value. The MAC is calculated before adding `mac`, which is correct, but callers must know that all original fields are included. Map iteration order is normalized by `url.Values.Encode`.

Test signals: `url_test.go` validates a fixed UUID-keyed query signature and encoded ordering.
