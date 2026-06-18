
# sources/distributed-fs/openafs/src/uss/uss_ptserver.h

Purpose: `uss_ptserver.h` declares the Protection Server interface for `uss`.

Important APIs: `uss_ptserver_AddUser()` creates or reconciles a PTS user and returns its UID string; `uss_ptserver_DelUser()` removes a PTS name; `uss_ptserver_XlateUser()` translates a name to numeric AFS UID.

Control flow and integration: add flow calls PTS creation before KAS creation and template parsing. delete flow translates before volume deletion and removes the PTS entry last.

State and persistence: implementation is lazily initialized and mutates the Protection Database unless dry-run is active for add/delete.

Risks and test signals: UID is returned through a caller-provided `char *`, so the caller must size it correctly. Tests should check ID collision semantics and delete idempotence.
