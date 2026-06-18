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
