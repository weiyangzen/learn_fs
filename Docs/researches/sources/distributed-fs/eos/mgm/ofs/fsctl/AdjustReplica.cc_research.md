## sources/distributed-fs/eos/mgm/ofs/fsctl/AdjustReplica.cc

Purpose: fsctl repair-on-close handler from FST/FUSE paths that dispatches replica adjustment through the user proc command interface.

Important APIs and types: `XrdMgmOfs::AdjustReplica`, `REQUIRE_SSS_OR_LOCAL_AUTH`, `ProcCommand`, root `VirtualIdentity`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: requires SSS or local authentication, marks write access, applies stall/redirect, switches identity to root, reads `mgm.path` from the environment, constructs `mgm.cmd=file&mgm.subcmd=adjustreplica&mgm.path=<path>&mgm.format=fuse`, opens and closes `/proc/user`, records stats, returns an `EIO` message if the proc command failed or path was missing, otherwise responds `OK` as `SFS_DATA`.

State and persistence behavior: the handler itself only changes the local `vid` to root and invokes proc infrastructure. Actual replica repair state changes happen in the file adjustreplica command.

Dependencies and integration points: intended for trusted local/SSS callers, likely FST repair-on-close flows. Depends on `/proc/user` command parsing and implementation of `file adjustreplica`.

Risks: root identity means the proc command bypasses caller permissions after authentication gate. The original `path` argument is used only for redirect macros; actual target comes from `mgm.path`. Error code is collapsed to `EIO` for proc failures, losing details.

Test signals: auth rejection for non-SSS/non-local, missing `mgm.path`, proc success response, proc failure mapped to `EIO`, root identity use, and command string format.
