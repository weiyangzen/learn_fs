# sources/distributed-fs/ceph-client/fs/smb/common/smbglob.h

Purpose: declares shared SMB dialect capability metadata and small NetBIOS/RFC1001 length helpers used by SMB client and server code. It is a lightweight common header rather than a runtime module.

Important APIs/types/functions: `struct smb_version_values` captures dialect-specific strings, protocol IDs, lock command encodings, capability flags, maximum read/write/transaction sizes, credits, lock type constants, header and response sizes, signing policy, and create-context sizes. `get_rfc1002_len()` extracts the 24-bit length from the 4-byte stream header, while `inc_rfc1001_len()` increments that header. Version strings include SMB 1.0, SMB 2.0, 2.1, 3.0, 3.0.2, 3.1.1, default, and SMB3-any aliases.

Control flow: callers use the selected dialect's `smb_version_values` after negotiate to size requests and responses and to encode command-specific fields. Receive paths use `get_rfc1002_len()` before allocating a request buffer; response builders use `inc_rfc1001_len()` as iovecs are appended.

State and persistence behavior: there is no state in the header. The structure instances live in dialect tables elsewhere and become per-connection configuration once negotiation completes.

Dependencies and integration points: depends on endian helpers. Integrates with SMB dialect negotiation, stream transport framing, request-size checks, credit accounting, locking behavior, signing policy, and create-context parsing.

Risks: RFC1002 length helpers assume a 4-byte accessible buffer and operate on big-endian stream headers; using them on an SMB header pointer instead of the transport header corrupts parsing. Dialect values control maximum I/O sizes and create-context lengths, so stale metadata can cause undersized buffers or noncompliant negotiation.

Test signals: negotiate each supported dialect, validate stream length parsing for boundary values, build compound responses with multiple iovecs, verify advertised max I/O sizes and credits, and test signing-required/enabled behavior across dialect versions.
