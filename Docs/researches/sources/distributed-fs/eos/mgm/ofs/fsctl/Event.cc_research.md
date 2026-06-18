<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc

Source read size: 234 lines, 8604 bytes.

## Purpose

Implements `XrdMgmOfs::Event`, the fsctl endpoint used to trigger EOS workflow events from FUSE or other MGM control clients. It reconstructs a workflow identity from opaque environment fields, checks the caller can perform the requested event on the target path, loads file/container metadata and attributes, and calls `Workflow::Trigger`.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::Event(const char*, const char*, XrdOucEnv&, XrdOucErrInfo&, VirtualIdentity&, const XrdSecEntity*)`. Important inputs are `mgm.ruid`, `mgm.rgid`, `mgm.sec`, `mgm.logid`, `mgm.path`, `mgm.fid`, `mgm.event`, `mgm.workflow`, and optional base64 `mgm.errmsg`. It uses `VirtualIdentity`, `SecEntity::KeyToMap`, `Mapping::*To*Name`, `Workflow`, `IFileMD`, `IContainerMD`, and attribute maps.

## Control Flow

The function builds a local identity from env overrides, sets the thread log id if present, chooses `P_OK` for prepare-like events and `W_OK` otherwise, and runs `_access` unless the caller uses `sss`. After write-mode access, stall, and redirect macros, it validates required env fields. It resolves metadata by fid or path under `FsView::gFsView.ViewMutex`, copies parent container attributes, optionally overlays attributes from `sys.attr.link`, initializes the workflow with attributes/path/fid, decodes a synchronous error message, and triggers the requested event/workflow. Missing workflows, internal errors, and nonzero workflow return codes are translated to `Emsg`; success returns `SFS_DATA` with `OK`.

## State and Persistence Behavior

No persistent state is owned here. It reads namespace metadata and xattrs under read locks, temporarily mutates local variables for template workflows beginning with `eos.`, and delegates durable side effects to workflow handlers. Thread-local logging state may be updated through `tlLogId`.

## Dependencies and Integration Points

Integrates fsctl request handling with `XrdMgmOfs`, MGM access macros, `FsView`, namespace services, workflow configuration under `MgmProcWorkflowPath`, xattr inheritance, base64 decoding, stats (`MgmStats.Add("Event")`), and `Workflow::Trigger`.

## Risks and Edge Cases

`spath` is used for access before the required-field block, so malformed calls without `mgm.path` depend on `_access` behavior. The prepare test is substring-based. Attribute-link failures are logged but do not abort, which may hide misconfiguration. Template workflows rewrite `spath` and reset fid, so callers must understand that metadata lookup changes. Base64 decode failure clears the synchronous error message.

## Test Signals

Exercise successful prepare and write events, permission failures for non-`sss` identities, fid and path lookup, `eos.*` template workflows, missing workflow `ENOKEY`, sync and async workflow failure handling, `sys.attr.link` inheritance, malformed env calls, and base64 `mgm.errmsg` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc -->
