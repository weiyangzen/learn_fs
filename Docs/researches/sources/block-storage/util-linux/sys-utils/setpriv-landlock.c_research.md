# File Research: sources/block-storage/util-linux/sys-utils/setpriv-landlock.c

This file implements the Landlock-specific support used by `setpriv(1)`. It provides syscall fallbacks for `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self` when libc does not expose wrappers.

The parser supports `--landlock-access fs` or `fs:<rights>` and path-beneath rules of the form `path-beneath:<rights>:<path>`. Rights map to `LANDLOCK_ACCESS_FS_*` constants, including conditionally compiled newer rights such as `refer`, `truncate`, and `ioctl-dev`. Empty right lists mean all known filesystem rights.

`do_landlock()` creates a ruleset with the requested handled filesystem accesses, adds all parsed path-beneath rules using `O_PATH` parent fds, sets `PR_SET_NO_NEW_PRIVS`, then restricts the current process. Landlock failures use setpriv’s privilege-error exit code `127`.
