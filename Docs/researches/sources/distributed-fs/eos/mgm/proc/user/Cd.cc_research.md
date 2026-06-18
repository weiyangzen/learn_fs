# sources/distributed-fs/eos/mgm/proc/user/Cd.cc

## Purpose

`Cd.cc` implements the legacy `ProcCommand::Cd()` command. It validates that a requested path exists and is a directory, enabling clients to change their working directory in the EOS shell/client layer.

## Important APIs, Types, and Functions

The only function is `int ProcCommand::Cd()`. It records command usage with `gOFS->MgmStats.Add("Cd", uid, gid, 1)`, reads `mgm.path` and `mgm.option`, applies `NAMESPACEMAP`, enters `PROC_TOKEN_SCOPE`, and calls `gOFS->_stat()`.

## Control Flow

The command maps the requested path, rejects an empty path with `EINVAL`, stats the mapped path, and returns the MGM error text and `errno` if stat fails. If stat succeeds, it checks `S_ISDIR`; directories set `retc` to 0, while non-directories return `ENOTDIR`. The function itself returns `SFS_OK` so the command transport can carry `retc` and `stdErr`.

## State and Persistence

`Cd()` does not mutate namespace state. It reads metadata and updates only command statistics and response fields. Any actual client working-directory persistence is outside this command, based on the success response.

## Dependencies and Integration Points

It depends on `ProcInterface`, `XrdMgmOfs`, `Macros`, and `Stat`. It uses the same path mapping and token-scope machinery as other legacy `/proc/user` commands.

## Risks and Test Signals

The command is intentionally small; main risks are path mapping/token behavior and ensuring the returned transport status remains `SFS_OK` while command status is in `retc`. Test signals include empty path, nonexistent path, regular file path, directory path, permission/token failures in `_stat`, and stats counter increment.
