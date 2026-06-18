# sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror.c

## Purpose
`smb1maperror.c` maps SMB1 DOS/SRV class errors and NTSTATUS errors into Linux negative errno values. It also validates generated mapping tables at init time and exposes lookup wrappers to KUnit tests.

## Important APIs, types, and functions
The primary APIs are `map_smb_to_linux_error`, `map_and_check_smb_error`, and `smb1_init_maperror`. Internal binary search helpers are `search_ntstatus_to_dos_map`, `search_mapping_table_ERRDOS`, and `search_mapping_table_ERRSRV`, with comparators for NTSTATUS and SMB error codes. Generated maps are included from `smb1_err_dos_map.c`, `smb1_err_srv_map.c`, and `smb1_mapping_table.c`.

## Control flow
`map_smb_to_linux_error` returns success for zero status. If the header uses NT status, it first maps NTSTATUS to a DOS class/code and logs selected errors; otherwise it reads the legacy DOS error class/code directly. DOS and SRV classes are binary-searched in their mapping tables. Unmapped or hardware-class errors default to `-EIO`, with additional special cases for `NT_STATUS_NOT_A_REPARSE_POINT` and `NT_STATUS_PRIVILEGE_NOT_HELD`. `map_and_check_smb_error` additionally detects legacy `ERRbaduid` and signals reconnect.

## State and persistence
The mapping tables are static read-only state. Runtime side effects are diagnostic logging and reconnect signaling for session identity errors. There is no persisted state.

## Dependencies and integration points
It depends on SMB1 header definitions, Samba-derived mapping data, NT error constants, `__inline_bsearch`, CIFS logging, reconnect signaling, and the SMB1 transport error path. `smb1ops.c` registers `map_smb_to_linux_error` as the dialect `map_error` operation.

## Risks and test signals
Risks include generated tables becoming unsorted, incomplete NTSTATUS coverage collapsing to `-EIO`, special-case status mappings bypassed by DOS fallback, and reconnect not triggered for status-form authentication failures. Test signals include init sortedness checks, KUnit lookup coverage over every table entry, malformed unknown status codes, `ERRbaduid` reconnect behavior, and reparse/privilege special cases.
