# sources/cloud-native/containers-storage/pkg/unshare/unshare.c

Purpose: Linux C constructor implementation that performs early namespace unshare and reexec before Go code starts.

Important APIs/types/functions: `_containers_unshare`, `_containers_unshare_parse_envint`, `_check_proc_sys_file`, `parse_proc_stringlist`, `try_bindfd`, `copy_self_proc_exe`, and `containers_reexec`.

Control flow: constructor reads `_Containers-unshare`; if absent it returns. It unshares user namespace first, writes child PID to the parent pipe, waits on the continue pipe for parent UID/GID map setup, optionally calls `setsid`, `setpgrp`, and `TIOCSCTTY`, sets uid/gid to 0 inside new userns, unshares remaining namespace flags, then reexecs the current binary via a protected bind-mounted fd or sealed memfd copy.

State/persistence: mutates process namespaces, uid/gid, session/process group, controlling terminal, environment variables, and can temporarily create a `/tmp/containers.XXXXXX` mount point/file.

Dependencies/integration: driven by environment and file descriptors set in `unshare_linux.go` `Cmd.Start`. Integrates with `/proc`, Linux clone flags, memfd sealing, mount APIs, and reexec behavior.

Risks: this is security-sensitive process bootstrap code. It exits the process on parse/syscall/setup errors. Reexec fallback must avoid writable executable fds; failure to detach temporary bind mounts is treated as unrecoverable. It prints diagnostics to stderr and checks kernel userns sysctls only after unshare failure.

Test signals: `unshare_test.go` validates namespace changes and ID mappings from the Go side; lower-level C paths are indirectly covered by successful reexec and synchronization.
