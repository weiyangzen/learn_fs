## sources/cloud-native/buildkit/util/gitutil/gitobject/parse.go

Purpose: parses raw Git commit/tag objects, extracts headers, message, signatures, signed payload, actors, and verifies object checksums.

Important APIs/types: `GitObject{Type,Headers,Message,Signature,SignedData,Raw}`, `Actor`, `Commit`, `Tag`. Functions/methods: `Parse`, `Checksum`, `VerifyChecksum`, `ToCommit`, `ToTag`, and internal `parseActor`.

Control flow: `Parse` identifies tags by `object ` prefix; otherwise treats input as commit. It reads headers until the blank line, handles multi-line commit `gpgsig` and `gpgsig-sha256` by collecting signature lines while excluding them from `SignedData`, and for tags treats PGP/SSH signature blocks after the message as detached signature text. It validates required headers by type. `Checksum` prefixes raw data with `commit <len>\0` or `tag <len>\0`. `VerifyChecksum` chooses SHA-1 or SHA-256 by expected length. Converters copy first/slice header values into typed structs. `parseActor` uses last angle brackets and optional Unix timestamp plus numeric timezone.

State/persistence: in-memory parsing only. Dependencies: crypto SHA-1/SHA-256, hex, time, `pkg/errors`.

Integration points: used by signature verification and Git provenance/trust code. Risks: object type inference is narrow; commit SSH signatures in headers are collected like PGP but test coverage focuses on PGP; malformed actor timezone hour/minute digits are ignored if `Atoi` fails, yielding zero offsets. Test signals: `parse_test.go` covers signed commit, signed tag, checksums, conversion, and actor edge cases.
