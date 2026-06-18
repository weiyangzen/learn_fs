# sources/distributed-fs/ceph-client/include/linux/fs_pin.h

Purpose: defines the small VFS pin object used to attach killable references to superblocks and mounts. Pins let teardown paths find and kill outstanding objects that are tied to a filesystem or mount lifecycle.

Important APIs and types: `struct fs_pin` contains a waitqueue, completion flag, hlist nodes for superblock and mount lists, and a `kill` callback. `init_fs_pin()` initializes the waitqueue and list nodes and installs the callback. `pin_insert()`, `pin_remove()`, and `pin_kill()` are implemented out of line.

Control flow: users initialize a pin with a subsystem-specific kill callback, insert it against a `vfsmount`, and remove or kill it during teardown. `pin_kill()` invokes the callback and coordinates with waiters through the embedded waitqueue and `done` flag.

State and persistence: pins are in-memory lifetime state only. They protect resources that may indirectly refer to persistent filesystem data by ensuring teardown sees and drains them.

Dependencies and integration points: depends on wait queues, hlist nodes, and `vfsmount`. It integrates with superblock `s_pins` and mount pin lists.

Risks and test signals: risks are list corruption, missed wakeups, double kill/remove, and callbacks that sleep or recurse in invalid contexts. Tests should stress unmount with active pins, concurrent remove/kill, callback failure behavior, and leak detection after namespace teardown.
