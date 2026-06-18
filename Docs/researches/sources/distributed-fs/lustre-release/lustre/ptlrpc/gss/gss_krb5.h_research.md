# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5.h

Purpose: defines Kerberos mechanism constants, token header layout, context state, checksum/signature algorithms, and supported encryption type identifiers for Lustre's GSS Kerberos implementation.

Important APIs/types/functions: RFC 4121 usage constants identify acceptor/initiator seal/sign keys. `struct krb5_header` is the 16-byte MIC/wrap header with token id, flags, filler, EC/RRC, sequence, and checksum tail. `struct krb5_ctx` tracks initiator/CFX/subkey flags, expiry, seed, send/receive sequences, enctype, encryption/integrity/checksum keyblocks, and mechanism OID. Constants define token ids, flags, checksum types, Kerberos error values, and supported AES enctypes.

Control flow: no executable code. `gss_krb5_mech.c` fills and verifies these headers while importing user-space contexts and performing MIC/wrap/bulk crypto.

State/persistence: declares per-context in-memory state. Imported keys and sequence numbers are held in `struct krb5_ctx`.

Dependencies/integration: includes `gss_crypto.h` for keyblocks. Interfaces with user-space Kerberos context serialization and Linux crypto algorithm selection.

Risks/test signals: header endianness and sequence semantics are wire-visible. Tests should verify supported enctype mapping, header size assumptions, initiator/acceptor direction flag behavior, token id constants, and context import compatibility with both older RFC1964-style and newer RFC4121-style serialized contexts.
