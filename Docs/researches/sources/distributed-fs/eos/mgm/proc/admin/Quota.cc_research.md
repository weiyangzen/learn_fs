# sources/distributed-fs/eos/mgm/proc/admin/Quota.cc

## Purpose
`Quota.cc` implements the legacy opaque-parameter `ProcCommand::AdminQuota()` path for quota administration. In this file the only supported subcommand is quota node removal.

## Important APIs, Types, And Functions
`ProcCommand::AdminQuota()` reads `mSubCmd`, `pVid`, and `pOpaque`, sets inherited `retc/stdOut/stdErr`, and calls `Quota::RmSpaceQuota(path, msg, retc)` for `rmnode`.

## Control Flow
For `mSubCmd == "rmnode"`, the function requires uid 0, reads `mgm.quota.space` from the opaque request, rejects an empty path, and delegates removal to `Quota::RmSpaceQuota()`. Success places the returned message in `stdOut`; failure places it in `stdErr`. Unknown subcommands return `EINVAL` with an error string. The function always returns `SFS_OK` because proc command transport success is separated from command `retc`.

## State, Persistence, And Dependencies
The persistent effect is deletion of quota-node state through `Quota::RmSpaceQuota()`. The file depends on `ProcInterface`, the global MGM object include, and `mgm/quota/Quota.hh`. Authorization uses the virtual identity pointer from the legacy proc command object.

## Integration Points
This is the old admin command path, parallel to the newer protobuf `QuotaCmd::RmnodeSubcmd()`. It is reached by opaque proc requests rather than `QuotaProto`.

## Risks
The authorization rule here is stricter than `QuotaCmd.cc`, allowing only uid 0 while the protobuf path permits uid 0 or 3. Input is a raw opaque string and path normalization is not performed here. Only `rmnode` is implemented, so callers expecting parity with protobuf quota commands will get `EINVAL`.

## Test Signals
Exercise root and non-root `rmnode`, missing `mgm.quota.space`, successful and failed `Quota::RmSpaceQuota()` returns, and unknown subcommands. Regression tests should compare legacy and protobuf behavior intentionally because their authorization differs.
