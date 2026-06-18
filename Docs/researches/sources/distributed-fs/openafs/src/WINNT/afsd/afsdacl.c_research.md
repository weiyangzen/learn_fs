# sources/distributed-fs/openafs/src/WINNT/afsd/afsdacl.c

## Purpose

`afsdacl.c` is a small Windows command-line utility for inspecting or changing the service DACL on `TransarcAFSDaemon`. It can grant ordinary users start/stop/read-control access through the `Everyone` ACE while ensuring `AFS Client Admins` receives broad service rights, or revoke the `Everyone` ACE.

## Important APIs, Types, and Functions

- Constants define actions `SETDACL` and `RESETDACL`, service name `TransarcAFSDaemon`, group names `AFS Client Admins` and `Everyone`.
- `show_usage()` prints CLI syntax for `-set`, `-reset`, and `-show`.
- `show_last_error()` formats Windows errors through `FormatMessage()`.
- `set_dacl(int action)` opens the SCM and AFSD service, queries the current DACL, builds two `EXPLICIT_ACCESS` entries, merges them with `SetEntriesInAcl()`, and writes the new DACL with `SetServiceObjectSecurity()`.
- `show_dacl()` opens the service, reads the DACL, converts it to SDDL with `ConvertSecurityDescriptorToStringSecurityDescriptor()`, and prints it.
- `main()` parses mutually exclusive `-set`/`-reset` plus optional `-show`.

## Control Flow

The tool parses arguments, requires at least one action or show request, applies `set_dacl()` first if requested, then calls `show_dacl()` if requested. Both service operations use a two-step `QueryServiceObjectSecurity()` pattern: first call for required size, allocate a descriptor, second call to populate it, then process or display the DACL.

## State and Persistence Behavior

The only persistent change is the Windows service object's discretionary ACL. `-set` grants `Everyone` `SERVICE_START | SERVICE_STOP | READ_CONTROL`; `-reset` revokes that entry. Both modes set `AFS Client Admins` to `SPECIFIC_RIGHTS_ALL | STANDARD_RIGHTS_ALL`. No repository files are modified.

## Dependencies and Integration Points

The utility depends on Windows SCM, ACL APIs, SDDL conversion, heap/local allocation, and localized account/group names. It is operationally tied to the service name used by `afsd_service.c`.

## Risks

- `rv` is initialized to `1` in both `set_dacl()` and `show_dacl()` and is never set to success, so the program appears to exit with failure even when operations succeed.
- Localized Windows installations may not resolve literal `Everyone` or `AFS Client Admins` names as expected.
- The code logs errors but continues after some failures such as `SetEntriesInAcl()` or `SetSecurityDescriptorDacl()`, risking a later write with invalid or stale ACL data.
- `QueryServiceObjectSecurity()` has an `else : shouldn't happen` path where `psdesc` can remain NULL before `GetSecurityDescriptorDacl()`.
- Granting service start/stop to `Everyone` is intentionally broad and should be treated as a security-sensitive deployment choice.

## Test Signals

- CLI tests should assert usage failures, mutually exclusive `-set`/`-reset`, combined action plus `-show`, and correct process exit codes.
- ACL tests should verify exact ACE additions/removals using SDDL before and after each action.
- Negative tests should cover missing service, insufficient privileges, unresolved group names, and allocation failures.
