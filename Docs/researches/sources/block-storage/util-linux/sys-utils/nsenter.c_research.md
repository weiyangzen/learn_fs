# File Research: sources/block-storage/util-linux/sys-utils/nsenter.c

This file implements `nsenter(1)`, a command-line wrapper for `setns(2)` and related process setup. It can enter mount, UTS, IPC, network, PID, cgroup, user, and time namespaces from a target PID, explicit namespace path, namespace ID, socket fd, or parent user namespace, then execute a requested program or shell.

Namespace state is represented by `namespace_files[]`, whose order is significant because user namespaces may need to be entered before or after other namespaces depending on whether privileges are being gained or reduced. The implementation supports pidfd-based multi-namespace `setns()` on newer kernels, fd-by-fd fallback, namespace ID lookup via nsfs file handles and `open_by_handle_at()`, and network namespace discovery from a target process socket with `pidfd_getfd()` and `SIOCGSKNS`.

After entering namespaces, the command can chroot to the target root, set cwd either from the target or inside the entered namespace, import the target environment, set UID/GID or follow the target process’s credentials, preserve credentials, retain ambient capabilities for user namespaces, set SELinux exec context, and join the target cgroup v2 by writing to `cgroup.procs`.

Important behavior: entering PID namespaces defaults to forking so the command runs as a child in the new PID namespace. `--all` skips unusable namespaces, including reentering the current user namespace. Namespace entry happens in two passes: non-user namespaces first with ignored errors, then remaining namespaces with fatal errors.
