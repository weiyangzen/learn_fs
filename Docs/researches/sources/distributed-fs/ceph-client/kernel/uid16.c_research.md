<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.c -->
# sources/distributed-fs/ceph-client/kernel/uid16.c

Purpose: implements legacy 16-bit UID/GID compatibility syscalls by translating between `old_uid_t`/`old_gid_t` and modern kernel uid/gid values.

Important APIs: syscall wrappers include `chown16`, `lchown16`, `fchown16`, `setregid16`, `setgid16`, `setreuid16`, `setuid16`, `setresuid16`, `getresuid16`, `setresgid16`, `getresgid16`, `setfsuid16`, `setfsgid16`, `getgroups16`, `setgroups16`, `getuid16`, `geteuid16`, `getgid16`, and `getegid16`. Helpers `groups16_to_user()` and `groups16_from_user()` convert supplementary group arrays.

Control flow: setter syscalls translate low 16-bit IDs with `low2highuid()` or `low2highgid()` and delegate to common credential syscalls declared in `uid16.h`. Getter syscalls map kernel credentials through the current user namespace using `from_kuid_munged()`/`from_kgid_munged()`, then truncate through `high2low*()` before copying to userspace. Group setting validates `may_setgroups()`, bounds by `NGROUPS_MAX`, allocates group info, converts each user gid with `make_kgid()`, sorts, and installs.

State and persistence: no independent state is stored here; all persistent effects are credential, ownership, or group changes performed by shared kernel helpers.

Dependencies and integration: depends on highuid conversion macros, user namespace id mapping, group_info allocation, and user access helpers. It exists only for architectures/configurations still exposing old 16-bit syscalls.

Risks: truncation and overflowuid/overflowgid behavior are compatibility-sensitive. Group conversion must reject unmapped gids. Test signals include legacy ABI syscall tests with mapped and unmapped IDs, invalid userspace pointers, negative group sizes, setgroups denial in user namespaces, and namespace overflow mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.c -->
