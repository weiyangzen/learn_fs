# sources/distributed-fs/ceph-client/fs/smb/client/smberr.h

## Purpose
`smberr.h` defines legacy SMB error classes and SMB error-code constants with comments indicating intended POSIX errno mappings. It supports code that maps SMB/CIFS protocol errors to Linux errors and documents server-originated DOS/SRV/HRD/CMD status classes.

## Important APIs, Types, And Functions
The header defines `struct smb_to_posix_error { __u16 smb_err; int posix_code; }` and constants for error classes `SUCCESS`, `ERRDOS`, `ERRSRV`, `ERRHRD`, and `ERRCMD`. It then lists DOS-class errors such as `ERRbadfunc`, `ERRbadfile`, `ERRbadpath`, `ERRnoaccess`, `ERRbadfid`, `ERRbadshare`, `ERRfilexists`, `ERRdiskfull`, `ERRdirnotempty`, pipe errors, quota/link errors, and internal passthrough values. It also lists SRV-class errors such as `ERRerror`, `ERRbadpw`, `ERRbadtype`, `ERRaccess`, `ERRinvtid`, `ERRinvnetname`, timeout/resource/user-account errors, and `ERRnosupport`.

## Control Flow
There is no executable logic. Mapping code can include this header to build error translation tables using the constants and the errno guidance embedded in comments.

## State And Persistence Behavior
The header stores no runtime state. It defines stable numeric protocol constants that must match legacy SMB wire values.

## Dependencies And Integration Points
It integrates with SMB/CIFS status-to-POSIX mapping code and with paths that still handle older SMB error-class/error-code responses rather than NTSTATUS-only SMB2 statuses. It complements SMB2 status mapping headers in `../common/smb2status.h`.

## Risks
The constants are protocol ABI. Renumbering or deduplicating them would break error mapping. Some values are obsolete or internal passthrough values; consumers must distinguish wire-originated values from internal-only translation aids. Comments are used to generate or reason about mapping tables, so stale comments can become behavior drift.

## Test Signals
Error mapping unit tests, KUnit SMB status tests, legacy server interop, DFS referral error mapping, pipe error handling, quota/link errors, and static checks that table entries use valid class/code pairs are relevant.
