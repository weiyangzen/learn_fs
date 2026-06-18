## sources/distributed-fs/ceph-client/fs/smb/server/unicode.h

Purpose: exposes ksmbd Unicode conversion helpers and pulls in the SMB/CIFS Unicode constants and Linux NLS/unicode types needed by server path and name handling.

Important APIs and types: declares `smb_strtoUTF16`, `smb_strndup_from_utf16`, `smbConvertToUTF16`, and `ksmbd_extract_sharename`. Includes byteorder, Linux types, NLS, Unicode, and UCS-2 utility definitions.

Control flow: callers convert local names to UTF-16 for responses, duplicate UTF-16 request strings into local codepage strings, and extract share names from tree-connect requests via the declared helper implemented in `misc.c`.

State and persistence behavior: no state is owned. Returned strings from duplication/extraction helpers are heap allocations owned by callers.

Dependencies and integration points: used by SMB1/SMB2 request parsing, directory response emission, short-name generation, tree connect handling, and misc path helpers. It bridges server code to shared NLS utilities under `fs/smb/nls`.

Risks: declarations expose byte-length based APIs; mismatched length units are a common integration hazard. The duplicate declaration of `ksmbd_extract_sharename` with `misc.h` means signature changes must stay synchronized.

Test signals: compile coverage of all users, UTF-16 round trips across codepages, tree-connect share-name extraction, and caller ownership/error handling for `ERR_PTR` returns.
