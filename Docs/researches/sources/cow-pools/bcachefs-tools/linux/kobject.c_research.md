# File Research: sources/cow-pools/bcachefs-tools/linux/kobject.c

Implements in-memory kobject/sysfs and debugfs shims. Kobjects track refs, parent/child arrays, normal attributes, binary attributes, and root registration under a global mutex. `sysfs_read_or_html_dirlist()` reads attributes or renders directory listings; `sysfs_write()` dispatches store/write callbacks.

Debugfs is represented by `debugfs_dentry` trees and can lazily start an HTTP server for per-filesystem debugfs creation.
