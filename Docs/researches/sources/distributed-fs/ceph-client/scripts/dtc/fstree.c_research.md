# sources/distributed-fs/ceph-client/scripts/dtc/fstree.c

Purpose: imports a filesystem directory tree as a DTC live device tree, with directories becoming nodes and regular files becoming properties.

Important APIs/functions: `read_fstree()` recursively opens a directory, skips `.` and `..`, stats entries, reads regular files with `data_copy_file()` into `build_property()`, descends into subdirectories, names child nodes with their directory entry names, and appends properties/children. `dt_from_fs()` names the root node `""`, computes boot CPU ID with `guess_boot_cpuid()`, and returns `build_dt_info(DTSF_V1, NULL, tree, ...)`.

Control flow/state: no persistent state beyond the constructed `struct node` graph. Processing order follows directory iteration order, so deterministic output depends on later sorting if callers require it.

Dependencies/integration: uses POSIX `opendir`, `readdir`, `stat`, `fopen`, and DTC tree/data helpers from `dtc.h`. It integrates with the same `dt_info` pipeline used by DTS and DTB inputs.

Risks: unreadable regular files are warned and skipped, while `opendir`/`stat` failures are fatal. Non-regular non-directory entries are ignored. Property names come directly from filenames, so invalid device-tree property names are not filtered here.

Test signals: directory-to-node recursion, file contents preserved as property bytes, unreadable file warning behavior, symlink/device entry handling, root naming, and downstream sort behavior.
