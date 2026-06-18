# sources/cloud-native/ostree/src/libostree/ostree-repo-os.c

Purpose: derives standard metadata for bootable OSTree commits from a root filesystem tree.

Important APIs/types/functions: implements `ostree_commit_metadata_for_bootable(GFile *root, GVariantDict *dict, GCancellable *cancellable, GError **error)`.

Control flow: the function opens `usr/lib/modules` under the supplied root, iterates child directories, and looks for a `vmlinuz` file inside each directory. If exactly one kernel module directory with `vmlinuz` is found, it inserts `ostree.bootable=true` and `ostree.linux=<kernel release>` into the caller's `GVariantDict`. It errors if no kernel is found or if multiple kernels are present.

State and persistence: no repository state is touched. The caller-owned metadata dictionary is updated in memory; later commit code persists those keys into commit metadata.

Dependencies/integration: depends on GIO file enumeration, `OSTREE_GIO_FAST_QUERYINFO`, libglnx error prefixing, and constants declared in `ostree-repo-os.h`. Intended for commit/build code that wants to mark bootable OS commits.

Risks: the heuristic assumes bootable commits have exactly one kernel in `/usr/lib/modules/<release>/vmlinuz`. Multi-kernel images fail deliberately. Missing `usr/lib/modules` or permission errors surface as open failures. The check uses `g_file_query_exists` without passing the caller cancellable for the nested `vmlinuz` query.

Test signals: no direct test appeared in the searched subset. Useful coverage would include no-kernel, one-kernel, multi-kernel, non-directory children, and metadata dictionary assertions.
