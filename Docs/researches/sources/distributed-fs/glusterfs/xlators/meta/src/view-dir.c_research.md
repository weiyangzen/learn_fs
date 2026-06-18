# sources/distributed-fs/glusterfs/xlators/meta/src/view-dir.c

Purpose: provides the placeholder `view` directory beneath an xlator entry. In this source it contains only dot entries and no dynamic fill callback.

Important APIs/types/functions: `view_dir_dirents` contains `.` and `..`; `meta_view_dir_hook()` propagates parent context and attaches `view_dir_ops`.

Control flow: lookup of `view` under an xlator directory installs a directory whose readdir returns only dot entries through default directory handling.

State and persistence behavior: no persistent or dynamic state is maintained. Parent xlator context is stored even though this file does not currently use it.

Dependencies and integration points: included as a fixed child in `xlator-dir.c`, likely reserving a namespace for future or external view entries.

Risks and edge cases: users may expect meaningful contents from `view` because it is exposed, but this implementation is empty. Future additions must preserve existing lookup semantics.

Test signals: lookup and readdir of `view`, ensuring it behaves as an empty directory and does not return errors.
