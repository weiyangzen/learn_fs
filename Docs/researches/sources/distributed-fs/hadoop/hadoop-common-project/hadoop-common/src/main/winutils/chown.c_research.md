<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c

## Purpose
`chown.c` implements the Windows `winutils chown` subcommand. It parses Hadoop's Unix-like owner/group argument form and delegates the actual owner/group ACL update to the shared `ChownImpl` helper.

## Important APIs, Types, And Functions
The exported entry point is `int Chown(int argc, wchar_t *argv[])`; `ChownUsage()` documents `OWNER[:GROUP] FILE`. The key internal values are `ownerInfo`, `pathName`, `colonPos`, and optional heap-allocated `userName` and `groupName`. It uses `StringCchCopyNW` for bounded copying, `LocalAlloc`/`LocalFree` for temporary names, and `ChownImpl(userName, groupName, pathName)` from the common winutils layer.

## Control Flow
`Chown` requires at least three arguments and uses `argv[1]` as the owner/group spec and `argv[2]` as the path. If a colon exists, text before the colon becomes `userName` unless empty, and text after the colon becomes `groupName` unless empty. If there is no colon, the full string becomes `userName`. Empty owner and empty group is a no-op success, matching cases such as `:`. Otherwise, the command calls `ChownImpl`; a nonzero return keeps the process exit status as failure.

## State And Persistence Behavior
The file itself holds no persistent state. Filesystem ownership or group ownership is changed by `ChownImpl`, likely through Windows security descriptors and owner/group SIDs declared in `winutils.h`. Temporary strings are freed before return. Unlike Unix, `user:` does not change the group to the user's login group; the usage text documents that Windows has no such login-group concept and leaves group unchanged.

## Dependencies And Integration Points
`chown.c` depends on `winutils.h` for Windows headers, string/error helpers, and `ChownImpl`. It is invoked through `winutils.exe chown` and supports Hadoop components that need to mimic POSIX ownership operations on Windows local files.

## Risks
The code ignores extra arguments beyond `argv[2]` because it checks only `argc >= 3`; callers expecting strict command-line validation may miss malformed invocations. `StringCchCopyNW` is called with destination lengths that include the null terminator, but the group/no-colon copy passes the full allocated length as the character count, which is safe because the source is null terminated yet slightly imprecise. Owner/group names depend on Windows account resolution elsewhere, so domain/local account ambiguity and privilege requirements are primary operational risks. Partial owner-only or group-only changes must be validated in `ChownImpl`.

## Test Signals
Tests should cover `owner file`, `owner:group file`, `owner: file`, `:group file`, `: file`, missing arguments, extra arguments, Unicode/domain-qualified account names, nonexistent users/groups, insufficient privileges, and ACL verification after owner-only and group-only changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c -->
