<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h

## Purpose
`winutils.h` is the shared public header for Hadoop's Windows utility executable and service support code. It centralizes Windows includes, exit codes, Unix-to-Windows permission constants, subcommand prototypes, security/ACL helpers, Kerberos/LSA token helpers, service helpers, configuration parsing, RPC/service security utilities, and process/job naming helpers.

## Important APIs, Types, And Functions
The header forces Unicode builds, includes core Windows/security headers (`windows.h`, `aclapi.h`, `accctrl.h`, `lm.h`, `ntsecapi.h`, `userenv.h`), and exposes `extern "C"` for C++ consumers. `enum EXIT_CODE` defines shared return codes including `SUCCESS`, `FAILURE`, `SYMLINK_NO_PRIVILEGE`, `ERROR_TASK_NOT_ALIVE`, and Unix-compatible `KILLED_PROCESS_EXIT_CODE` 137. `enum UnixAclMask` defines POSIX mode bits for owner/group/other read/write/execute plus directory/regular/symlink file-type bits. `enum WindowsAclMask` indexes `WinMasks[]` for read/write/execute/owner/all Windows ACL masks.

Command APIs include `Ls`, `Chmod`, `Chown`, `Groups`, `Hardlink`, `Task`, `Symlink`, `Readlink`, `SystemInfo`, and service entry/usage functions. Filesystem/security helpers include `GetFileInformationByName`, `CheckAccessForCurrentUser`, `ConvertToLongPath`, SID/account conversion, `FindFileOwnerAndPermission`, directory/symlink/junction checks, `ChangeFileModeByMask`, file/directory creation with mode, `ChangeFileOwnerBySid`, and `ChownImpl`. Identity and service helpers include local-group lookup, DLL name lookup, privilege enabling, LSA string registration/unregistration, Kerberos package lookup, logon token/profile loading, impersonation privileges, service security descriptor construction, adding NodeManager/user ACEs, and secure job object naming. Utility APIs include timestamp/logging, string splitting, module-relative path building, and XML config lookup.

## Control Flow
As a header, this file has no runtime control flow. It defines the call graph contract followed by individual command files and shared implementation units. `winutils.exe` dispatches subcommands to the declared command functions; command implementations call the shared helpers for path conversion, Windows account/SID resolution, ACL translation, and error reporting. Service-related code uses the LSA, token, profile, and security descriptor APIs to run tasks as users and protect job/process objects.

## State And Persistence Behavior
Declared functions operate on persistent Windows state: file ACLs and owners, directories/files created with modes, symlinks/junctions, local group membership queries, privileges in process tokens, LSA logon sessions, user profiles, job objects, service security descriptors, process/object ACEs, and configuration values read from XML. The header also declares constants used to map persistent Windows ACLs into Hadoop's Unix-style permission model.

## Dependencies And Integration Points
This header is the integration spine for the Windows-specific Hadoop Common native code. It ties together `chmod.c`, `chown.c`, `groups.c`, `hardlink.c`, RPC client/service files, task launching, symlink/readlink, local filesystem ACL emulation, and Hadoop Java callers that shell out to `winutils.exe`. It depends on Windows-only APIs and is not portable to Unix builds. The XML config functions connect service/native code to Hadoop configuration files, while Kerberos/LSA helpers connect Hadoop identity to Windows authentication.

## Risks
Because this header exposes broad privileged operations, API contract drift can break multiple commands or the service. SAL annotations help static analysis but do not enforce runtime null/length checks. The Unix permission mask abstraction is necessarily lossy relative to Windows ACLs, so callers may assume POSIX semantics that the underlying ACL helpers cannot fully provide. Exit code overlap exists (`FAILURE`, `ERROR_TASK_NOT_ALIVE` both map to 1), which can limit diagnostic precision. Any change to `WinMasks[]` semantics affects chmod, file creation modes, and permission reporting across Hadoop on Windows.

## Test Signals
Test signals include native compilation in C and C++ translation units, static analysis of SAL contracts, unit tests for Unix/Windows ACL mask translation, long path conversion, SID/account round trips, owner/group/mode discovery, chmod/chown/file creation behavior, symlink/junction checks, service security descriptor construction, privilege enabling, LSA/Kerberos token creation, user profile load/unload, and integration tests through Java Hadoop filesystem APIs on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h -->
