# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-dcache.c

Purpose: verifies `/proc/net` follows the current network namespace after `setns()` even when `/proc/net/unix` was already cached in dcache.

Important APIs and functions: uses `unshare(CLONE_NEWNET)`, `socket(AF_UNIX)`, `fork`, pipe synchronization, `/proc/$pid/ns/net`, `setns`, and readback of `/proc/net/unix`.

Control flow: parent enters one netns and creates a UNIX socket as a distinguisher. Child enters a second netns and pauses. Parent opens child's netns fd, opens `/proc/net/unix` to pin old dentry, switches to child netns, kills child, and reads `/proc/net/unix`, requiring only the header line.

State and persistence: transient namespaces, socket, and child process. `atexit` kills the child if needed.

Dependencies and integration: requires network namespaces, UNIX sockets, proc net entries, and setns permission.

Risks and test signals: `CONFIG_UNIX` is required despite a FIXME. Failure indicates cached proc net dentries are not namespace-aware after setns.
