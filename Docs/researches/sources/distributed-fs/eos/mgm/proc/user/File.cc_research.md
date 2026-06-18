# sources/distributed-fs/eos/mgm/proc/user/File.cc

## Purpose

`File.cc` is a large legacy `ProcCommand::File()` dispatcher for file-level operations: dropping, moving, copying, replicating, verifying, retagging, changing layout, sharing, renaming, symlinking, triggering workflows, scheduling conversions, touching/locking files, adjusting replica counts, returning metadata locations, and managing file versions.

## Important APIs, Types, and Functions

The single entry point is `int ProcCommand::File()`. It uses many `gOFS` APIs: `_dropstripe`, `_movestripe`, `_copystripe`, `_replicatestripe`, `_verifystripe`, `_touch`, `_stat`, `_access`, `_attr_ls`, `_chmod`, `rename`, `symlink`, `_rename_with_symlink`, `PurgeVersion`, `Version`, `CreateSharePath`, `QueryResync`, and namespace service accessors. It also integrates `LayoutId`, `Resolver`, `Quota::FilePlacement`, `Scheduler::FileAccess`, `Policy::GetPlctPolicy`, `ConverterEngine::ScheduleJob`, `ConversionTag`, `XattrLock`, and XRootD `CopyProcess`.

## Control Flow

The command first resolves `mgm.file.id` to a path when provided; otherwise it maps `mgm.path`. All subcommands set `cmdok` when recognized, and unrecognized subcommands end with `EINVAL`. Privileged branches such as `layout`, `verify`, `tag`, and `adjustreplica` require root or daemon identity. Replica operations delegate to scheduling or stripe APIs. `copy` builds source/target lists for files or directory trees and performs local root:// third-party copy jobs. `convert` validates layout/space/policy/checksum arguments, derives target conversion tags, and schedules work in QuarkDB. `touch` can create/truncate/absorb files, set hardlink/checksum info, and acquire or release xattr locks. Version branches copy current content into `.sys.v#` storage, purge old versions, list versions through `ls`, or stage a selected version back.

## State and Persistence

This file mutates core file metadata and data-plane state: layout ids, replica locations and unlinked locations, conversion jobs, share paths, namespace names, symlink entries, workflow events, xattr locks, touched file metadata, version directories, and scheduled verification/resync/replication jobs. Several branches take explicit namespace or filesystem-view locks; others rely on lower-level `gOFS` APIs. Asynchronous work is scheduled into MGM services, filesystems, or QuarkDB rather than completed inline.

## Dependencies and Integration Points

`File()` is an integration hub for the MGM: access control macros, path/id resolution, namespace metadata services, filesystem view, quota placement, scheduler, converter engine, policy, xattr lock manager, XRootD copy, checksum utilities, file-id helpers, and other proc commands (`file convert`, `file copy`, `ls`) via nested `ProcCommand` calls. It bridges user requests to both metadata operations and data movement.

## Risks and Test Signals

The blast radius is high. Risks include inconsistent partial updates after scheduling failures, privilege mistakes, stale metadata around explicit lock release, id/path confusion, targetfsid parsing in `move` depending on the source string length check, duplicated HTTP path append in `share`, copy behavior for empty files versus TPC, and complex replica-adjustment placement/drop decisions. Test signals should cover every subcommand, root versus non-root authorization, fid and path addressing, layout constraints, verify with filters/resync/alt checksums, share expiry limits, rename identifier resolution, tag add/remove/unlink, recursive directory copy, convert rewrite and placement policy validation, touch lock/unlock wildcard behavior, replica under/over-replication, version create/list/grab/purge, and unknown subcommands.
