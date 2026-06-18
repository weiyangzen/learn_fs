# sources/distributed-fs/ceph-client/fs/smb/client/smbencrypt.c

## Purpose
`smbencrypt.c` contains legacy SMB/CIFS password hashing support. In this listed slice it implements NT MD4 password hashing used to produce the 16-byte NT hash from a password converted to NT Unicode.

## Important APIs, Types, And Functions
The exported function is `E_md4hash(const unsigned char *passwd, unsigned char *p16, const struct nls_table *codepage)`. It converts at most 128 password characters to UTF-16 with `cifs_strtoUTF16`, hashes the UTF-16 byte stream through the internal `mdfour` helper, writes the digest to `p16`, and explicitly zeros the temporary UTF-16 password buffer.

The internal `mdfour` helper wraps `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final` from the common MD4 implementation and logs failures.

## Control Flow
If `passwd` is non-null, `E_md4hash` converts it to UTF-16; if null, it hashes an empty null-terminated buffer. It then calls `mdfour`, clears `wpwd` with `memzero_explicit`, and returns the crypto helper status. `mdfour` performs init/update/final in order and exits early on init/update failures.

## State And Persistence Behavior
No persistent state is stored. The sensitive temporary Unicode password is stack-allocated and explicitly cleared. The resulting hash is written to the caller-provided output buffer.

## Dependencies And Integration Points
The file depends on CIFS Unicode conversion, debug helpers, common MD4, NLS tables, and kernel crypto/FIPS-related headers. It integrates with legacy authentication code that needs NT password hashes.

## Risks
MD4/NT hashes are legacy and security-sensitive. Callers must avoid using this in contexts where stronger authentication is required. The 128-character conversion limit can truncate longer inputs. Output buffer sizing is caller-owned, so callers must provide at least 16 bytes. Any edits must preserve `memzero_explicit` of password material.

## Test Signals
Known NT hash test vectors, null/empty password behavior, non-ASCII password conversion under different NLS tables, crypto helper failure injection, and static analysis for sensitive buffer clearing are relevant.
