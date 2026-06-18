<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c

## Purpose
`hardlink.c` implements the Windows `winutils hardlink` subcommand. It supports creating a hard link to an existing file and reporting the number of hard links for a file.

## Important APIs, Types, And Functions
`HardLinkCommandOptionType` defines `HardLinkInvalid`, `HardLinkCreate`, and `HardLinkStat`. The exported entry point is `int Hardlink(int argc, wchar_t *argv[])`, with `HardlinkUsage()` documenting `hardlink create LINKNAME FILENAME` and `hardlink stat FILENAME`. Internal helpers are `ParseCommandLine`, `HardlinkStat`, and `HardlinkCreate`. The implementation uses shared `ConvertToLongPath`, `GetFileInformationByName`, and `ReportErrorCode` helpers, plus the Windows `CreateHardLink` API.

## Control Flow
`ParseCommandLine` requires exactly three args for `hardlink stat` or four for `hardlink create`, and also requires `argv[0]` to equal `hardlink`. For `stat`, the command converts the file path, reads `BY_HANDLE_FILE_INFORMATION`, and prints `nNumberOfLinks`. For `create`, it converts both link and target paths, calls `CreateHardLink(longLinkName, longFileName, NULL)`, and prints a success message on completion. Any conversion, file-information, or API failure is reported and returns process failure.

## State And Persistence Behavior
`stat` is read-only. `create` persists a new directory entry pointing to the same file data on the same volume. Temporary long-path strings are allocated and freed with `LocalFree`. There is no rollback needed beyond the single `CreateHardLink` call.

## Dependencies And Integration Points
The file depends on `winutils.h` for path conversion, file information, and error reporting. It integrates with Hadoop's Windows shell utilities where Java code expects hard-link functionality analogous to Unix `ln` or link-count inspection.

## Risks
`CreateHardLink` works only for files on volumes/filesystems that support hard links and generally requires source and link on the same volume; errors are surfaced but not interpreted. The strict `argv[0] == "hardlink"` check can fail if a dispatcher passes a full executable name or command alias instead of the subcommand name. `HardlinkStat` uses `followLink=FALSE`, so behavior on symlink paths depends on how `GetFileInformationByName` handles reparse points. The success message includes paths and may expose sensitive local paths in logs.

## Test Signals
Tests should cover successful create/stat on NTFS, cross-volume create failure, missing source, existing link path, directory input, symlink/reparse point input, long paths, Unicode paths, strict argument validation, and expected link count changes through both winutils and native Windows APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c -->
