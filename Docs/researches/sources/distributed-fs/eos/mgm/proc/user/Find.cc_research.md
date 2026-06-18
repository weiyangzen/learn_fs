# sources/distributed-fs/eos/mgm/proc/user/Find.cc

Purpose: implements the legacy `/proc/user` `find` handler as `ProcCommand::Find()`. It traverses namespace paths, optionally filters files and directories, formats results, calculates replica balance summaries, and can trigger version or atomic-file purge side effects.

Important APIs and types: reads request fields from `pOpaque` (`mgm.path`, `mgm.option`, `mgm.find.*`), maps paths through `NAMESPACEMAP`, enforces `PROC_BOUNCE_*` and `PROC_TOKEN_SCOPE`, writes via temporary output files, calls `gOFS->_exists`, `gOFS->_find`, `_stat`, `_rem`, `_attr_ls`, `_attr_get`, and `PurgeVersion`, and inspects metadata through `gOFS->eosView`, `IFileMD`, `IContainerMD`, `FsView`, `Acl`, `LayoutId`, and checksum helpers.

Control flow: after option parsing, shallow whole-namespace-like searches are marked as `deepquery` and serialized by a static mutex around a shared `globalfound` map. The handler checks target existence, runs `_find`, iterates directory map entries and their file sets, applies file filters such as zero size, mixed scheduling groups, replica count mismatch, age windows, and output options, then optionally prints counters or balance summaries. Directory results are handled in a second pass for ACL checks, child counts, attributes, version purge, and `fileinfo -m` delegation.

State and persistence: normal operation is read-only except statistics and output files. `--purge` can remove old version directories with `PurgeVersion`, and `purge=atomic` can delete atomic temporary files older than one day if the caller is root or owns the file. Balance maps are process-local, while `globalfound` is static and reused after clearing.

Dependencies and integration: tightly coupled to `XrdMgmOfs`, namespace metadata locking, `FsView` filesystem inventory, ACL validation, and legacy `ProcCommand` dispatch. It delegates rich file metadata output by opening another `/proc/user` command.

Risks: destructive options are embedded in a search command, deep searches serialize globally and use shared mutable state, and output formatting is hand-built. Filters and counters are interleaved, which makes behavior sensitive to option combinations. Metadata exceptions are mostly logged and skipped, so partial results may look successful. Test signals should cover path mapping and token scope, deep query locking, large output behavior, purge authorization and age thresholds, mixed scheduling groups, replica mismatch selection, ACL validation, balance output, and `fileinfo -m` delegation.
