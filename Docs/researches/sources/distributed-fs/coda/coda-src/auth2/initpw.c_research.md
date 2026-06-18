# sources/distributed-fs/coda/coda-src/auth2/initpw.c

## Purpose
One-shot conversion tool for generating initial auth2 password-file records from tab-separated cleartext input. It hex-encodes the fixed-size password key, optionally XOR-encrypting it with a supplied file key.

## APIs, Types, and Functions
`main()` parses `-x debuglevel` and `-k key`, initializes LWP, reads stdin lines, calls `parse()`, optionally invokes `rpc2_Encrypt(..., RPC2_XOR)`, and prints transformed records. `parse()` splits `<ViceId>\t<clear-password>\t<rest>`, zero-pads an `RPC2_EncryptionKey`, and returns the uninterpreted tail.

## Control Flow, State, and Persistence
Input is processed line by line. The first tab is replaced with NUL so the original line buffer becomes the ViceId field printed back by `main()`. The clear password is copied until tab, NUL, or key length, then the remaining tail is preserved. The tool writes only stdout; the caller redirects output to the password database.

## Dependencies and Integration
Depends on RPC2 encryption types, LWP initialization, and the auth2 password-file format consumed by `pwsupport.c`. It exists for bootstrapping `db/auth2.pw`.

## Risks and Test Signals
Risks include cleartext passwords on stdin, fixed 1000-byte input lines, aborting on malformed lines, `strncpy()` of the key without guaranteed full initialization for short values, and the intentionally weak XOR file-key transform. Test signals are stable hex output, unchanged trailing fields, warning when no key is supplied, and successful loading by `InitPW()`.
