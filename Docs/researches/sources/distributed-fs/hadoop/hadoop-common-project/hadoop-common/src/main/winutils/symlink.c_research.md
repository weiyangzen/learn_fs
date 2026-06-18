# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/symlink.c

Purpose: implements `winutils symlink`, creating Windows symbolic links while enforcing Hadoop-specific path and privilege checks.

Important APIs/functions: `Symlink` converts link and target to long paths, rejects forward-slash separated paths, enables `SeCreateSymbolicLinkPrivilege`, checks target directory status with `DirectoryCheck`, then calls `CreateSymbolicLinkW`; `SymlinkUsage` documents return code `2` for missing privilege.

Control flow: accepts exactly link name and target. Any conversion or validation failure exits through cleanup. Directory targets set `SYMBOLIC_LINK_FLAG_DIRECTORY`; file targets use zero flags.

State and persistence: creates a filesystem symlink and writes diagnostics. It does not change ACLs directly but depends on token privilege adjustment.

Dependencies/integration: depends on `ConvertToLongPath`, `EnablePrivilege`, `DirectoryCheck`, and `ReportErrorCode` from the shared library; dispatched by `main.c`; output is consumed by Hadoop tests and Windows filesystem integrations.

Risks and test signals: symlink privilege differs by Windows policy and developer mode; rejecting `/` paths prevents unusable links but may surprise callers. Tests should cover no privilege, file target, directory target, forward-slash rejection, missing target directory check errors, and exact return codes.
