# sources/distributed-fs/eos/mgm/proc/user/Chown.cc

## Purpose

`Chown.cc` implements the legacy `ProcCommand::Chown()` command for changing owner and optionally group on files and directories. It supports recursive operation, symlink no-dereference behavior, username/group-name translation, and safeguards around assigning root ownership.

## Important APIs, Types, and Functions

The main function is `int ProcCommand::Chown()`. It reads `mgm.path`, `mgm.chown.option`, and `mgm.chown.owner`. It uses `_find`, `_stat`, `_chown`, `eos::common::Path`, and `eos::common::Mapping::UserNameToUid` / `GroupNameToGid`.

## Control Flow

After mapping and token setup, the command rejects missing path or owner. Option containing `r` recursively populates a directory-to-files map with `_find`. Non-recursive mode stats the path; directories are stored as directory entries, while files are represented as parent directory plus filename and set `singlefile`. The owner string is split on `:`. Missing uid or gid components are represented by `0xffffffff` to mean unchanged. Names are translated unless explicitly `0`. Non-root callers may not change either uid or gid to 0. The command then applies write access mode, updates directories unless this is a single-file operation, and updates all files in the map, stripping any `" -> "` symlink display suffix before mutation.

## State and Persistence

Persistent state is file and container ownership metadata. `nodereference` from option `h` is passed to `_chown` to control symlink handling. Recursive state comes from `_find`; partial failures update `retc` but the command continues through later entries.

## Dependencies and Integration Points

The command integrates with legacy command macros, namespace stat/find/chown APIs, EOS identity mapping, and XRootD mode types. Although stored under `proc/user`, the header comment still says `proc/admin/Chown.cc`, reflecting its administrative nature.

## Risks and Test Signals

Name translation failures and root-ownership checks are central. The use of `owner.find(":")` into an `int` and `STR_NPOS` deserves boundary coverage. Output formatting differs for root and non-root users, and one file-success path only appends a newline inside the root branch. Tests should cover `uid`, `uid:gid`, `:gid`, root ids as non-root, recursive mixed files/directories, symlink suffix stripping, `-h`, translation errors, and partial failure continuation.
