# sources/distributed-fs/openafs/src/util/fstab.c

Purpose: Provides Darwin-specific compatibility implementations for fstab-style iteration over mounted filesystems using `getfsstat()`.

Important APIs: Under `AFS_DARWIN_ENV`, defines `mntinfo(struct statfs **mntbuffer)`, `getfsent()`, `setfsent()`, and `endfsent()`. These mimic BSD fstab iteration while exposing current mount information.

Control flow and state: `setfsent()` frees any previous static mount buffer, calls `mntinfo()` to allocate and populate a `statfs` array, and initializes static cursor state. `getfsent()` builds a static `struct fstab` view over the current `statfs` entry, sets read-only/read-write type from flags, advances the cursor, and decrements count. `endfsent()` releases the buffer and resets static state.

Dependencies and integration: Darwin-only code includes `<sys/mount.h>` and `<fstab.h>`. This supports code that expects fstab APIs on platforms where the mounted filesystem list is the relevant source.

Risks and test signals: Static global cursor state is not thread-safe. `mntinfo()` stores allocation in a static `origbuf` but `setfsent()` manages `mntbuf`, so ownership is implicit. Error paths call `err(1, ...)`, which exits the process. Test signals are platform build and filesystem enumeration behavior on Darwin.
