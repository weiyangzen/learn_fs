# sources/distributed-fs/openafs/src/dvolser/Makefile.in

This Makefile builds the demand-attach volume server `davolserver`. It compiles selected `volser`, `dir`, and `vol` sources with `-DRXDEBUG`, `-DFSSYNC_BUILD_CLIENT`, and `-DAFS_DEMAND_ATTACH_FS`, then statically links them with command, ACL, RX, rxstat, rxkad, LWP compatibility, util, opr, usd, hcrypto, roken, and platform libraries.

State is generated objects and the `davolserver` binary. Control flow is explicit make rules for each borrowed source, followed by install/dest staging to server libexec or destination server bin directories. Integration is with demand-attach volume operations, volume salvage/sync clients, and the directory package.

Risks include shared-source compile flag drift, static link ordering, and demand-attach-specific behavior depending on fssync/salvsync client definitions. Test signals are successful link, volume create/delete/dump/restore/move operations, vol_split coverage, and directory salvage operations under davolserver paths.
