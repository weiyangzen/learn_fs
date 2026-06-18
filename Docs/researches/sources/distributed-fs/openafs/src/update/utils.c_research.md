
# sources/distributed-fs/openafs/src/update/utils.c

`utils.c` implements the update package's simple `struct filestr` linked-list helpers. `AddToList` allocates a node, pushes it at the head of a caller-owned list, and stores a `strdup` of the supplied name. `ZapList` walks the list, frees each name and node, and resets the head to `NULL`.

There is no persistence beyond heap ownership. Dependencies are `global.h`, libc allocation, and platform includes for NT builds. The functions are used heavily by `upclient` to manage configured directories, modified files, and host manifest entries.

Risks are small but real: allocation failures are not checked, `AddToList` always returns 0, and callers rely on LIFO order being acceptable. Test signals are memory-leak/error-injection checks and repeated `ZapList` calls in the synchronization loop.
