<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h

Purpose: declares the OCFS2 DLM debugging interface and provides no-op debugfs hooks when debugfs support is disabled.

Important APIs and types: `dlm_print_one_mle()` is always declared for diagnostic paths in mastering/recovery code. When `CONFIG_DEBUG_FS` is enabled, `struct debug_lockres` stores seq-file iteration state (`dl_len`, `dl_buf`, pinned `dl_ctxt`, and current `dl_res`) and the header declares `dlm_debug_init()`, `dlm_create_debugfs_subroot()`, `dlm_destroy_debugfs_subroot()`, `dlm_create_debugfs_root()`, and `dlm_destroy_debugfs_root()`. When debugfs is disabled, those lifecycle hooks compile to empty inline functions.

Control flow: no runtime control flow beyond the inline stubs. The header lets domain setup and teardown call debugfs hooks unconditionally, with build-time selection deciding whether files are created.

State and persistence behavior: only `struct debug_lockres` describes state, and that state exists per open debugfs seq file. The disabled path stores no state.

Dependencies and integration points: implemented by `dlmdebug.c`, consumed by `dlmdomain.c` for debugfs lifecycle and by `dlmmaster.c` for MLE diagnostics. It depends on DLM core type declarations being visible before inclusion.

Risks: any changes to `struct debug_lockres` must stay synchronized with the seq operations in `dlmdebug.c`. Stub behavior must remain side-effect free so domain lifecycle code is identical across debugfs and non-debugfs builds.

Test signals: compile both `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`; with debugfs enabled, verify per-domain files appear and disappear as domains are registered/unregistered; with it disabled, verify domain lifecycle links without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h -->
