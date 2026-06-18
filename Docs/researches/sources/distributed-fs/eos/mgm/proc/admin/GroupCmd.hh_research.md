# sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.hh

Purpose: Declares `GroupCmd`, the protobuf command wrapper for EOS MGM group administration.

Important APIs/types/functions: `GroupCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares private `LsSubcmd()`, `RmSubcmd()`, and `SetSubcmd()` helpers that accept generated `GroupProto` submessage types plus a mutable `ReplyProto`.

Control flow: The header defines a request-scoped command object with all behavior funneled through `ProcessRequest()` and helper branches. The constructor passes `false` to the base command, matching other protobuf admin commands that do not use the special filesystem-command flag.

State and persistence behavior: No direct persistent state is stored in the object. The implementation mutates `FsView`, shared hashes, and geotree placement config.

Dependencies and integration points: Includes `Namespace.hh`, `Group.pb.h`, and `ProcCommand.hh` for `IProcCommand`/reply helpers. It is used by MGM admin routing for `GroupProto` requests.

Risks: Any proto schema changes for group subcommands require synchronized signature and dispatch changes. The command exposes only three subcommands, so unsupported future oneof cases will return `EINVAL` until implemented.

Test signals: Construction, dispatch for ls/rm/set, unsupported oneof handling, and compile compatibility with generated `Group.pb.h`.
