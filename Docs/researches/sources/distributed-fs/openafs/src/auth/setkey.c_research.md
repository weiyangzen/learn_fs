# sources/distributed-fs/openafs/src/auth/setkey.c

## Purpose
Command-line utility for listing, adding, and deleting legacy rxkad server keys in the server configuration directory.

## Important APIs, Types, and Functions
`main` parses `add`, `delete`, and `list`. `char2hex` converts input hex digits to nibbles; `hex2char` converts output nibbles for listing. It calls `afsconf_Open`, `afsconf_AddKey`, `afsconf_DeleteKey`, and `afsconf_GetKeys`.

## Control Flow
After opening `AFSDIR_SERVER_ETC_DIRPATH`, `add` validates that the key argument is exactly 16 hex characters, packs it into 8 bytes, and writes with overwrite enabled. `delete` converts kvno with `atoi` and deletes it. `list` fetches legacy keys and prints printable key bytes and hex.

## State and Persistence
The tool mutates the server key files through the `afsconf` key APIs. It does not maintain its own state.

## Dependencies and Integration Points
Depends on auth cell configuration, `keys.h`, `rxkad`, and component version metadata. It is an operator/admin utility and is superseded for non-rxkad typed keys by newer key management paths.

## Risks and Test Signals
Invalid hex characters produce `-1` nibbles but are not rejected, so malformed input can silently generate unintended bytes. `atoi` accepts partial/non-numeric kvnos. Listing prints raw key bytes as a C string, which may contain control characters. Tests should cover invalid hex, kvno parsing, add/list/delete round trips, and error reporting from config open or key API failures.
