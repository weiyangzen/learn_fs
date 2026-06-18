## sources/distributed-fs/moosefs/mfsmaster/metadata.h

Purpose: declares the master metadata lifecycle API consumed by filesystems, changelog replay, supervisors, status handlers, and process startup/shutdown.

Important APIs: version and id management (`meta_version_inc`, `meta_version`, `meta_get_id`, `meta_set_id`, `meta_mr_setmetaid`), lifecycle (`meta_init`, `meta_cleanup`, `meta_restore`), runtime flags (`meta_setignoreflag`, `meta_allowautorestore`, `meta_emptystart`, `meta_incverboselevel`), explicit storage (`meta_do_store_metadata`), store/download status (`meta_download_status`, `meta_info`), and changelog retention floor (`meta_chlog_keep_version`).

Control flow and integration: startup code calls flag setters before `meta_init`; normal metadata mutations call `meta_version_inc`; replication replay calls the `mr` API; supervisors trigger explicit store; status code calls `meta_info`; changelog retention consults `meta_chlog_keep_version`.

State and persistence behavior: the header exposes controls for the persistent metadata file set managed in `metadata.c` but stores nothing itself. Return codes follow MooseFS status/error conventions for replay APIs.

Dependencies: includes `stdio.h` and fixed-width integers. It intentionally hides the metadata section list and subsystem load/store functions.

Risks: `meta_version_inc` increments global metadata version and should only be used on changes that are or will be changelogged/replayed. `meta_setignoreflag` and autorestore are powerful recovery switches that can allow metadata loss if used casually.

Test signals: compile coverage across startup, restore tools, changelog replay, and supervisor paths. Regression tests should assert metadata version/id updates and status reporting around save, download, and replay operations.
