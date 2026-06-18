# subset-b-007046 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Accounting.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Accounting.cc

## Purpose

`Accounting.cc` implements the legacy `ProcCommand::Accounting()` user command for EOS storage accounting. It exposes two subcommands: `config`, which lets sudoers tune the in-process accounting report cache, and `report`, which returns a JSON accounting document describing the storage service, capacity, and quota-backed storage shares.

## Important APIs, Types, and Functions

The main API is `int ProcCommand::Accounting()`. Internally it owns a static `eos::common::ExpiryCache<std::string>` with a default 600 second expiry and a static `generateAccountingJson(VirtualIdentity&)` lambda. The generator reads extended attributes through `gOFS->_attr_ls`, quota data through `Quota::GetAllGroupsLogicalQuotaValues()`, formats output with `Json::Value`, and returns a heap-allocated string for the cache to own. A nested `processAccountingAttribute` lambda recognizes keys prefixed with `sys.accounting`, splits dot-separated paths, creates nested JSON objects or array positions, and stores comma-separated values as JSON arrays.

## Control Flow

The command initializes `retc` to `SFS_OK`, then dispatches on `mSubCmd`. `config` first requires `pVid->sudoer`; it then parses `mgm.accounting.expired` and `mgm.accounting.invalid` as minute values, clamps them to minimums of 1 and 5 minutes, and updates the cache timing. `report` reads `mgm.option`, treats option `f` as force-refresh, and calls `accountingCache.getCachedObject(forceUpdate, generateAccountingJson, std::ref(*pVid))`. Unsupported subcommands return `ENOTSUP`.

## State and Persistence

Persistent source state comes from namespace xattrs under the MGM proc path and each quota path, especially `sys.accounting.*` metadata. Report state is cached in memory in a function-local static cache shared by all calls in the MGM process. Capacity and share usage are snapshots derived from quota state; no namespace state is mutated by `report`. `config` mutates only cache policy, not persisted metadata.

## Dependencies and Integration Points

The command integrates `ProcCommand` opaque request parsing, the global MGM object `gOFS`, quota aggregation, JSONCPP, `StringTokenizer`, and EOS version macros. It is part of the `/proc/user` command surface and depends on the same `stdOut`, `stdErr`, `retc`, `pOpaque`, and `pVid` fields as other legacy commands.

## Risks and Test Signals

The JSON path builder trusts `sys.accounting.*` attribute structure; malformed numeric path components can create arrays, and unexpected short keys could index the last component. Values containing commas are always converted to arrays, which may surprise callers expecting scalar strings. The generator allocates a new string for the cache callback, so cache ownership semantics matter. Test signals include sudo and non-sudo `config`, invalid numeric inputs, forced and cached `report`, xattr-driven nested JSON, quota paths with share metadata, and error propagation as `EAGAIN` on cache update failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Accounting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/AclCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/AclCmd.cc

## Purpose

`AclCmd.cc` implements the protobuf-backed `AclCmd` command for listing and modifying EOS `sys.acl` and `user.acl` extended attributes. It converts between textual ACL rules and bitmasks, supports recursive directory updates, optional insertion positions, identifier translation, and read/write metadata locking around namespace objects.

## Important APIs, Types, and Functions

`AclCmd::ProcessRequest()` dispatches `AclProto::LIST` and `AclProto::MODIFY`. `GetAcls()` reads `sys.acl`, `user.acl`, and `sys.eval.useracl` from a `FileOrContainerMD`. `ModifyAcls()` parses the requested rule, resolves the target set, locks each metadata object, applies rule changes, and stores the new ACL xattr. Parsing helpers include `GetRuleFromString()`, `GenerateRuleMap()`, `GetRuleBitmask()`, `ParseRule()`, `CheckCorrectId()`, `ApplyRule()`, `GenerateAclString()`, `AclBitmaskToString()`, and `GetRulePosition()`.

## Control Flow

LIST prefetches the item, gets a read lock on either file or container metadata, extracts requested ACLs, converts numeric ids back to names best-effort with `Acl::ConvertIds`, and returns `ENODATA` if no ACL content is present. MODIFY validates the incoming rule first. User ACL modification additionally requires `sys.eval.useracl` for non-root users. Recursive mode calls `_find` to collect directories and skips EOS version directories; single-path mode may operate on either a file or a container. For each path, the command prefetches metadata, takes a write lock, reads current ACLs, turns them into an ordered `RuleMap`, validates requested insertion position, applies additions/removals/set semantics, serializes the map, and calls `gOFS->_attr_set` with a `FusexCastBatch`.

## State and Persistence

The persistent state is the `sys.acl` or `user.acl` xattr on target namespace entries. The in-command state is `mId`, `mAddRule`, `mRmRule`, and `mSet`, all derived from the rule string. Recursive modification can update many container ACL attributes. FUSE notifications are batched until metadata locks are released. Existing ACL order is preserved with `std::list<Rule>` and can be changed when a position is supplied.

## Dependencies and Integration Points

This command depends on `IProcCommand`, `proto/Acl.pb.h`, `mgm/acl/Acl.hh`, `gOFS->eosView`, `eos::Prefetcher`, metadata locking helpers, `gOFS->_find`, and `gOFS->_attr_get/_attr_set`. It integrates with EOS ACL identity conversion and namespace xattr semantics rather than POSIX mode bits.

## Risks and Test Signals

Parser edge cases are the highest-risk area: ACL strings use both `+` as an operation and as a permission prefix (`+d`, `+u`), `CheckCorrectId()` assumes enough characters for `id.at(1)`, and unknown permission characters in stored ACLs are ignored. Recursive updates are partially tolerant of missing directories but fail on other metadata exceptions. Test signals should cover list user/sys/both, set versus add/remove grammar, egroup and key ids, invalid ids, position insertion and moving existing entries, recursive updates over disappearing directories, user ACL rejection without `sys.eval.useracl`, and serialization order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/AclCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/AclCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/AclCmd.hh

## Purpose

`AclCmd.hh` declares the protobuf command class and small ordered-map utilities used by `AclCmd.cc`. Its role is to define the ACL rule representation, preserve ACL order during mutation, and expose selected parser helpers for unit testing.

## Important APIs, Types, and Functions

`Rule` is a `std::pair<std::string, unsigned long>` where the key is an ACL principal such as `u:123`, `g:45`, `egroup:name`, or `k:key`, and the value is a permission bitmask. `RuleMap` is a `std::list<Rule>` rather than a map so insertion position is stable and duplicate keys can be replaced without losing order. Utility templates include `key_position`, three `insert_or_assign` overloads, and `get_iterator`, which converts 1-based user positions into iterators.

## Control Flow

The `AclCmd` constructor forwards the request and identity to `IProcCommand` with write-intent enabled. `ProcessRequest()` is the command entry point. Public static helpers `GenerateRuleMap()`, `GetRuleFromString()`, and `GetRulePosition()` support parser tests. `GetRuleBitmask()` and `CheckCorrectId()` expose rule and id validation. Private methods split command behavior into xattr reads, path mutation, parsing, bitmask formatting, and application of parsed rules.

## State and Persistence

The header defines no persisted state, but it shapes persisted ACL encoding by assigning bit positions to textual ACL flags. The `ACLPos` enum covers read, write, execute, management, quota, creation, archive, sys ACL, sys attr, token, write-once, and negative or propagation flags. Instance fields `mId`, `mAddRule`, `mRmRule`, and `mSet` hold one parsed modification request.

## Dependencies and Integration Points

The class inherits from `IProcCommand`, consumes `eos::console::RequestProto`, uses `VirtualIdentity`, and depends on `proto/Acl.pb.h`. It is tightly coupled to EOS ACL string syntax and the `AclCmd.cc` parser. The utility templates are generic but live in this command header, so accidental broader use would inherit the list-based semantics.

## Risks and Test Signals

The custom `insert_or_assign` overload that moves an existing key adjusts the insertion iterator after erase; off-by-one behavior here would reorder ACLs incorrectly. `get_iterator` rejects position zero and positions beyond size. The enum uses `1 << 18` in an `unsigned long` target, which is safe for current values but should be watched if flags grow. Test signals include replacement without movement, movement to earlier and later positions, invalid positions, empty maps, and round-trip bitmask-to-string behavior for every enum flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/AclCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Archive.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Archive.cc

## Purpose

`Archive.cc` implements the legacy `ProcCommand::Archive()` command for managing EOS archive workflows. It creates archive manifests, marks archived subtrees immutable, submits put/get/purge/delete/kill/list requests to an external archiver daemon, and tracks archived directories through marker files and `/proc/archive` fast-find entries.

## Important APIs, Types, and Functions

`Archive()` is the command dispatcher. Listing helpers are `ArchiveFormatListing()`, `ArchiveUpdateStatus()`, and `ArchiveGetDirs()`. External control is done through `ArchiveExecuteCmd()` over a ZMQ REQ socket to `gOFS->mArchiveEndpoint`. Authorization is centralized in `ArchiveCheckAcl()`. Creation uses `ArchiveCreate()`, `ArchiveAddEntries()`, `MakeSubTreeImmutable()`, and `MakeSubTreeMutable()`. Static marker names include `.archive.init`, `.archive.put.done`, `.archive.put.err`, `.archive.get.done`, `.archive.get.err`, `.archive.purge.done`, `.archive.purge.err`, `.archive.delete.err`, and `.archive.log`.

## Control Flow

`transfers` and `kill` do not need a namespace path and only build JSON daemon commands. `list` maps the requested path and first asks the archiver for all transfers. Transfer operations map and validate the archive directory, require archive ACL permission, require a real directory, compute the directory inode, and build marker file paths. `create` validates archive destination configuration and MGM alias, checks that the destination hash directory does not already exist, makes the subtree immutable, and builds `.archive.init`. `put`, `get`, `purge`, and `delete` validate that the correct prior marker exists, or use failed markers in retry mode. Non-list operations call `ArchiveExecuteCmd`; list-style operations format daemon output and local pending backup state.

## State and Persistence

Archive state is represented by marker files inside the archived directory, a generated archive manifest copied into `.archive.init`, subtree `sys.acl` mutations containing `z:i`, and a fast-find file named by container id under `gOFS->MgmProcArchivePath`. Temporary manifest state is written under `gOFS->TmpStorePath` and removed after copy. Archive destination existence is checked through XRootD. The archiver daemon owns transfer progress outside this file.

## Dependencies and Integration Points

This command integrates global MGM configuration (`MgmArchiveDstUrl`, `MgmArchiveSvcClass`, `MgmOfsAlias`, `MgmProcArchivePath`), `Acl`, `NewfindCmd`, XRootD `XrdCl::CopyProcess` and `FileSystem`, ZMQ, namespace services, and `XrdMgmOfsDirectory`. `ArchiveAddEntries()` depends on `NewfindCmd` `fileinfo` monitoring output and parses key/value lines to produce manifest rows.

## Risks and Test Signals

The command has several consistency risks: making a subtree immutable can partially succeed; manifest creation failures attempt to restore mutability, but later copy/chmod/proc-entry failures may leave marker or ACL state behind. JSON requests are manually concatenated without escaping. `ArchiveAddEntries()` rejects zero-size files, symlinks (`xstype=none`), atomic files, and version paths, so archive eligibility depends on fileinfo output format. Tests should cover ACL denial, already archived subtrees, destination already exists, create rollback, malformed archiver replies, ZMQ timeout, retry marker validation, delete admin-only behavior, listing status reconciliation, and manifest parsing for paths with spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Archive.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Attr.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Attr.cc

## Purpose

`Attr.cc` implements the legacy `ProcCommand::Attr()` command for listing, reading, setting, removing, and folding EOS extended attributes. It supports path and numeric id addressing, recursive operation over directories, exclusive set mode, access checks, and special validation for layout-related attributes.

## Important APIs, Types, and Functions

`SanitizeXattr()` validates `sys.forced.blocksize` and `user.forced.blocksize` by base64-decoding the value and checking `LayoutId::IsValidBlocksize()`. `ProcCommand::Attr()` handles subcommands `ls`, `get`, `set`, `rm`, and `fold`. It uses `Resolver::retrieveFileIdentifier`, `GetPathFromFid()`, `GetPathFromCid()`, `_find`, `_access`, `_attr_ls`, `_attr_get`, `_attr_set`, and `_attr_rem`.

## Control Flow

The command maps the input path or resolves `fid/fxid/pid/pxid/cid/cxid` to a canonical path, unseals XRootD paths, enters token scope, validates subcommand and required xattr parameters, strips double quotes from values, and sanitizes selected keys. Recursive option `r` uses `_find` to collect target directories, falling back to the original path for file-like results; otherwise it operates on one path. Option `c` enables exclusive creation. `set` and `rm` switch to write access mode. Each target then executes the selected branch: `ls` lists visible attributes, `set` validates user ACL and `sys.attr.link` constraints, `get` reads one key, `rm` removes one key, and `fold` removes local attributes whose values match a linked origin.

## State and Persistence

The command persists xattr changes on namespace entries. `fold` can remove local copies based on `sys.attr.link` inheritance. `set sys.attr.link` requires the referenced value to be an existing directory. Recursive operations can update or inspect many directories and return after the first fatal access or validation error in several branches.

## Dependencies and Integration Points

`Attr()` integrates with EOS access macros, token scoping, namespace path mapping, `gOFS` xattr APIs, `Path`, `Resolver`, `IView`, and layout validation. It overlaps behavior with `AclCmd` for user ACL gating but uses the older opaque command interface.

## Risks and Test Signals

Because `Attr()` is a generic xattr mutation surface, validation coverage is intentionally narrow and most keys are trusted. Recursive mode only targets directory maps produced by `_find`, with a special fallback for files. `fold` shadows `retc` with a local variable in one branch, which can obscure error handling. Test signals include id-to-path resolution, invalid identifiers, recursive file fallback, exclusive set, user ACL rejection without `sys.eval.useracl`, `sys.attr.link` target validation, blocksize base64 validation, `ls -V`, binary-ish `sys.file.buffer` display, and fold behavior with matching and non-matching link attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Attr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Cd.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Cd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Chmod.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Chmod.cc

## Purpose

`Chmod.cc` implements the legacy `ProcCommand::Chmod()` command for changing EOS namespace mode bits on one path or recursively over a directory tree.

## Important APIs, Types, and Functions

The sole entry point is `int ProcCommand::Chmod()`. It reads `mgm.path`, `mgm.option`, and `mgm.chmod.mode`, maps the path, validates names and access through macros, optionally enumerates targets with `gOFS->_find`, and applies `gOFS->_chmod`.

## Control Flow

After path mapping and token setup, the command requires both path and mode. Option exactly equal to `r` enables recursive `_find`; otherwise it builds a single-entry target map. It validates the mode string by formatting `strtoul(mode, 10)` back as decimal text and comparing with the original, then interprets the value as base 8 for `XrdSfsMode`. It switches to write access mode and calls `_chmod` for each found directory path, producing success or error lines.

## State and Persistence

The persistent state is the mode on each target namespace entry. Recursive `_find` determines the set of directories to update; this implementation does not iterate the per-directory file sets from `_find`, so the visible mutation loop is over map keys.

## Dependencies and Integration Points

It integrates with EOS path mapping, illegal-name and access-bounce macros, recursive stall accounting, and `gOFS->_chmod`. It uses legacy opaque request fields and response buffers.

## Risks and Test Signals

Mode validation is subtle: the input must look like decimal digits, but is later parsed as octal, so strings like `755` pass and become octal `0755`; invalid octal digits may pass the decimal check and then be parsed by `strtoul(..., 8)` up to the invalid character. Non-root success output prepends `2` before the printed mode, matching EOS behavior but worth regression coverage. Test signals include empty mode/path, recursive and non-recursive updates, invalid mode strings, invalid octal digits, access denial, and partial recursive failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Chmod.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Chown.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Chown.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/DfCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/DfCmd.cc

## Purpose

`DfCmd.cc` implements the protobuf-backed `DfCmd` command body. It returns EOS filesystem capacity and usage information by delegating directly to `FsView::gFsView.Df()`.

## Important APIs, Types, and Functions

The only method is `eos::console::ReplyProto DfCmd::ProcessRequest() noexcept`. It extracts `eos::console::DfProto df = mReqProto.df()` and passes `df.monitoring()`, `df.si()`, `df.readable()`, `df.path()`, and `WantsJsonOutput()` to `FsView::gFsView.Df()`.

## Control Flow

The method constructs a reply, delegates formatting and data retrieval to `FsView`, stores the returned string as `std_out`, sets `retc` to 0, and returns. No local validation or exception handling is present in this file.

## State and Persistence

`DfCmd.cc` does not mutate state. It reads the current filesystem view through `FsView`; any freshness, locking, and filtering semantics are owned by that subsystem.

## Dependencies and Integration Points

It includes `DfCmd.hh`, `XrdMgmOfs`, `FsView`, and config headers. Its main integration point is the protobuf console request/reply command path, replacing older opaque-command style for `df`.

## Risks and Test Signals

The thin wrapper means risk is mostly contract drift with `DfProto` or `FsView::Df()`. Since `retc` is always 0, errors must be encoded by `FsView::Df()` if needed. Test signals include monitoring output, SI units, human-readable output, path filtering, JSON output, and behavior when the filesystem view is empty or partially unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/DfCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/DfCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/DfCmd.hh

## Purpose

`DfCmd.hh` declares the protobuf command class for `df` requests. It provides the type boundary between console `DfProto` requests and the `IProcCommand` asynchronous command framework.

## Important APIs, Types, and Functions

`class DfCmd : public IProcCommand` exposes a constructor taking `eos::console::RequestProto&&` and `VirtualIdentity&`, a default destructor, and `ProcessRequest() noexcept`. The constructor passes `false` as the final `IProcCommand` argument, indicating the command does not require write behavior.

## Control Flow

There is no local control flow beyond construction and virtual dispatch. The command framework calls `ProcessRequest()` implemented in `DfCmd.cc`.

## State and Persistence

The class stores no additional fields beyond inherited request and identity state. It declares no persistent behavior.

## Dependencies and Integration Points

The header depends on `mgm/Namespace.hh`, `proto/Df.pb.h`, `mgm/proc/ProcCommand.hh`, and `IContainerMD.hh`. It integrates with the same protobuf command framework used by `AclCmd`.

## Risks and Test Signals

The main risks are API compatibility and command classification. If `Df` ever needs authorization, path prefetching, or write-side effects, the constructor flag and implementation must change. Test signals are compile-time protobuf compatibility and runtime dispatch of `RequestProto.df()` into a successful reply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/DfCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/File.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/File.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Fileinfo.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Fileinfo.cc

## Purpose

`Fileinfo.cc` implements file and directory metadata reporting for legacy `ProcCommand::Fileinfo()`. It supports text, monitoring key/value, environment, and JSON output; path, fid/fxid, pid/pxid, and inode addressing; file health classification; filesystem-location tables; and recursive JSON children for directories.

## Important APIs, Types, and Functions

`FileMDToStatus()` classifies file state as `hardlink`, `symlink`, `healthy`, `pending_deletion`, `locations::uncommitted`, `locations::incomplete`, `locations::overreplicated`, or FUSE-related states. `Fileinfo()` resolves the input and dispatches to `FileInfo()`, `DirInfo()`, `FileJSON()`, or `DirJSON()`. `FileInfo()` and `DirInfo()` produce text or monitoring output. `FileJSON()` and `DirJSON()` build JSONCPP objects and can write to `stdJson` or an output parameter.

## Control Flow

`Fileinfo()` maps paths unless an id-style argument is used, stats normal paths to determine file versus directory, converts FUSE inode values when requested, and dispatches by `mJsonFormat`. `FileInfo()` prefetches file metadata by id or path, locks the namespace view, retrieves and clones metadata, releases the lock, and formats requested fields. Non-monitoring output supports filters such as `-path`, `-fxid`, `-fid`, `-size`, `-checksum`, `-fullpath`, and `-proxy`; `-m` produces key/value monitoring output; `-env` dumps the file environment. `DirInfo()` mirrors this for containers. JSON functions prefetch metadata with parents, optionally lock, clone/read metadata, attach xattrs, etags, locations, children, and error objects.

## State and Persistence

This command is read-only for namespace metadata. It reads file/container attributes, locations, unlinked locations, timestamps, layout ids, checksums, etags, tree counters, and filesystem snapshots. It may invoke scheduler access calculations for proxy display, but does not persist scheduling decisions.

## Dependencies and Integration Points

It depends on `gOFS` namespace services, `eos::Prefetcher`, `Resolver`, `FileId`, `LayoutId`, checksum and etag utilities, `FsView`, `Scheduler::FileAccess`, table formatter helpers, JSONCPP, and container iterators. `ArchiveAddEntries()` depends on the monitoring `fileinfo -m` shape, especially `keylength.file`, `file`, xattr pairs, size, timestamps, layout, and checksum fields.

## Risks and Test Signals

Output format stability is critical because other commands parse it. The monitoring parser must preserve paths with spaces via `keylength.file`. JSON directory recursion can be expensive on large trees. Locking is intentionally minimized by cloning metadata before formatting, so tests should watch for stale but safe snapshots. The status classifier depends on location counts, tape fsid, unlinked locations, and `sys.fusex.state` suffix parsing. Test signals include path/id/inode resolution, detached metadata, symlink targets inside and outside EOS, hardlinks, all filter options, monitoring output with xattrs and alt checksums, JSON errors, filesystem location tables, proxy display, unlinked locations, directory tree counters, and recursive JSON children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Fileinfo.cc -->
