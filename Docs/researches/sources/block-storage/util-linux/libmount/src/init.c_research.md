# File Research: sources/block-storage/util-linux/libmount/src/init.c

This file defines libmount debug subsystem initialization.

Key behavior:

- `UL_DEBUG_DEFINE_MASK(libmount)` and `UL_DEBUG_DEFINE_MASKNAMES(libmount)` define debug categories including cache, context, diff, fs, hook, locks, loop, options, optlist, table, update, utils, monitor, btrfs, and verity.
- `mnt_init_debug()` initializes the debug mask once, using the supplied mask or `LIBMOUNT_DEBUG` environment variable.
- When debugging is enabled beyond init/help, it logs library version and feature strings.
- Help debug prints supported masks.

Dependencies and interactions:

- All files use `DBG`, `DBG_OBJ`, and subsystem masks defined here.
- The optional test program parses a numeric mask and initializes debugging.

Risk notes:

- Debug initialization is one-shot; later calls cannot alter the mask once initialized.
