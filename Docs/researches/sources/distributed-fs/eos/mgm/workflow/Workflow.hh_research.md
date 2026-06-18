## sources/distributed-fs/eos/mgm/workflow/Workflow.hh

Purpose: Declares the `Workflow` helper that binds namespace xattrs, a path/file id, an event, and a workflow name into WFE job creation or callback CGI generation.

Important APIs and types: `Init` attaches an external xattr map and optional file identity; `SetFile` updates path/fid; `Trigger`, `getCGICloseW`, `getCGICloseR`, `Create`, and `ExceptionThrowingCreate` are the public workflow operations. `IsSync` checks the stored event prefix, and `Reset` clears all transient state.

Control flow: callers initialize with metadata attributes, optionally set a file, then trigger by event/workflow. The header intentionally keeps persistence details private behind `Create`, while static helpers query global WFE configuration.

State and persistence: stores a raw pointer to `IContainerMD::XAttrMap`, path, fid, current event, workflow, and action. It does not own the attribute map, so lifetime and locking are caller responsibilities.

Dependencies and integration: uses common file ids, `VirtualIdentity`, MGM namespace macros, and namespace `IView` types. The implementation integrates with `WFE` and MGM filesystem view globals.

Risks: raw xattr pointer can dangle or race if the caller releases metadata locks too early. `SetFile` ignores zero fid and empty path, which is convenient but can leave stale values if callers expected clearing. `IsSync` assumes `mEvent` has at least six characters but `substr` itself is safe.

Test signals: validate reset semantics, event prefix detection, path/fid retention rules, and trigger behavior when `mAttr` is null or lacks keys.
