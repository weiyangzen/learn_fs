# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.h

Purpose: Declares the RADOS bucket logging commit-manager API.

Important APIs/types/functions: `init()` starts the singleton commit manager for a `RadosStore` and `SiteConfig`. `shutdown()` stops it. `add_commit_target_entry()` records a pending log object for a target bucket/prefix and temp pool. `list_pending_commit_objects()` lists pending entries for a target bucket/prefix.

Control flow: Callers add commit targets during bucket logging write paths; the background manager later processes them. Listing is a diagnostic/helper path over the same commit-list object.

State/persistence: The API exposes persistent commit-list manipulation in the logging pool while hiding manager internals.

Dependencies/integration: Forward declares `SiteConfig`, SAL `RadosStore`, `DoutPrefixProvider`, and uses RGW pool and yield types through included project headers.

Risks: Header formatting leaves `list_pending_commit_objects()` less indented than the namespace block but functionally valid. The singleton lifecycle means tests and daemon startup/shutdown must avoid double init or leaked manager state.

Test signals: Link callers against the header, initialize/shutdown idempotency behavior, add/list consistency, and integration with bucket logging commit paths.
