# sources/distributed-fs/glusterfs/xlators/meta/src/name-file.c

Purpose: implements the virtual `name` file for an xlator entry in `.meta`, returning the target translator's runtime name.

Important APIs/types/functions: `name_file_fill()` retrieves an `xlator_t *` from inode context and writes `xl->name` plus newline to `strfd`. `meta_name_file_hook()` attaches `name_file_ops` and copies the parent xlator context to the child file.

Control flow: lookup of `name` under an xlator directory invokes the hook, then default readv calls `meta_file_fill()`, which calls `name_file_fill()`.

State and persistence behavior: no state is persisted. The file reflects the live `xlator_t` pointer stored by the parent `xlator-dir` hook and cached per open fd after read.

Dependencies and integration points: depends on `meta_ctx_get/set()`, `meta_ops_set()`, `strfd`, and the parent `xlator-dir.c` context contract.

Risks and edge cases: a missing or stale xlator context will dereference null or freed memory. Long-lived fds can cache an old name if graph state changes.

Test signals: traverse `.meta/.../<xlator>/name`, verify output matches the translator name, and test behavior across graph reloads or fd reopen.
