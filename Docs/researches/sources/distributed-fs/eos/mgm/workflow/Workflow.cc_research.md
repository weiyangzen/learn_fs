## sources/distributed-fs/eos/mgm/workflow/Workflow.cc

Purpose: Implements the metadata-driven workflow trigger surface used by MGM operations. It converts event/workflow names and namespace xattrs into `WFE::Job` actions, with special behavior for synchronous close/open workflows and WFE enablement flags.

Important APIs and functions: `Trigger` resolves `sys.workflow.<event>.<workflow>` attributes and invokes `Create`; `getCGICloseW` and `getCGICloseR` generate CGI query fragments for FST close callbacks; `Create` wraps `ExceptionThrowingCreate`; `WfeRecordingEnabled` and `WfeEnabled` read space configuration.

Control flow: `Trigger` normalizes some workflow names (`none`, retrieve-written, default), looks up the matching xattr key, stores the selected event/workflow/action, then calls `Create`. `ExceptionThrowingCreate` builds a `WFE::Job`; sync events run immediately when WFE is `on`, while async events are saved to queue `q` when WFE is not `off`.

State and persistence: `Workflow` itself only mutates transient members inherited from initialization, but async creation persists jobs through `WFE::Job::Save`. Sync closew CGI generation fetches file metadata and encodes custom attributes into a base64 parameter.

Dependencies and integration: depends on MGM global `gOFS`, namespace `Prefetcher`, `IView`, `FsView::gFsView` space configuration, `WFE`, `SymKey::Base64Encode`, and workflow constants. It must be called while metadata pointers and file ids are valid.

Risks: missing xattrs return `-1` with `errno=ENOKEY`, so callers must distinguish absent workflows from real failures. `getCGICloseW` fetches metadata and parent URI and can suppress workflow URL creation on `MDException`. WFE config semantics differ for sync (`wfe == on`) and async recording (`wfe != off`), which should be explicit in tests.

Test signals: test xattr key selection, sudo `none` handling, retrieve-written protocol fallback, enonet stall return, sync versus async job creation, exception-to-`ECANCELED` conversion, and CGI payload fields for closew/closer.
