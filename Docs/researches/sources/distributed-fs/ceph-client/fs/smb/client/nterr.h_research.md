# sources/distributed-fs/ceph-client/fs/smb/client/nterr.h

## Purpose
`nterr.h` defines NTSTATUS constants and the structure used for NTSTATUS-to-DOS error mapping. It is protocol vocabulary rather than executable logic, used by SMB status decoding and generated SMB1 mapping tables.

## Important APIs, types, and functions
The main type is `struct ntstatus_to_dos_err`, containing DOS error class, DOS code, NTSTATUS value, and string name. The file defines Win32-style helper constants such as `NT_ERROR_INVALID_PARAMETER`, then a large set of `NT_STATUS_*` values including success, pending, buffer overflow, access denied, object/path/file errors, sharing and lock failures, authentication/account failures, network errors, DFS path errors, reparse errors, encryption errors, and SMB negotiation/authentication statuses. Comments encode DOS class/code metadata for mapping generation.

## Control flow
There is no runtime control flow. Preprocessor definitions are consumed by C code and by table generation. The comments are semantically relevant because they document mapping pairs used to generate `smb1_mapping_table.c`.

## State and persistence behavior
The header stores no runtime state. It stabilizes constants that must match the SMB/Windows wire protocol and generated mapping artifacts.

## Dependencies and integration points
It is included by error mapping and network helper code such as `netmisc.c`, SMB1/SMB2 protocol handling, and status-to-errno conversion paths. Any change affects wire-status interpretation and user-visible errno behavior across the SMB client.

## Risks
Risks are incorrect constant values, duplicate or missing status definitions, comment/mapping drift that changes generated DOS mappings, and accidentally changing ABI-visible behavior for server errors. Because many constants are encoded as `0xC0000000 | value`, edits must preserve exact widths and values.

## Test signals
Regenerate and compare SMB1 mapping tables, compile all protocol configurations, verify representative status-to-errno conversions for access denied, object not found, path not covered, sharing violation, delete pending, not a reparse point, too many links, logon failure, and encryption errors, and run interoperability tests against Windows, Samba, and ksmbd servers that return these statuses.
