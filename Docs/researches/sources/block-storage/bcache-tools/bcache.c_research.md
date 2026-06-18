# File Research: sources/block-storage/bcache-tools/bcache.c

This is the main multi-command CLI, versioned as `bcache-tools 1.1`. It requires effective UID 0 for every subcommand, validates UUID and `/dev/...` paths with regular expressions, and dispatches to `make`, `show`, `tree`, `register`, `unregister`, `attach`, `detach`, `set-cachemode`, `set-label`, and `version`.

Most actions delegate to `make_bcache`, `show_*`, or `lib.c` sysfs helpers. `tree` builds an in-memory list of bcache devices and displays active cache devices with attached backing devices. `attach` accepts either a cache-set UUID or cache-device path, resolves cache devices to their cset UUID, ensures the target data device is not already attached, and writes to the backing device attach sysfs node.

Notable risk: fixed-size 4096-byte string assembly in `tree` and `replace_line` can overflow if many devices or long names are present.
