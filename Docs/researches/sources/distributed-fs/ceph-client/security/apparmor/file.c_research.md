# sources/distributed-fs/ceph-client/security/apparmor/file.c

## Purpose
`file.c` implements AppArmor file and open-file mediation: path permission checks, hardlink pair checks, audit formatting for file permissions, conditional owner permissions, per-file context caching, Unix/socket file revalidation, and inherited-file cleanup after domain transitions.

## Important APIs and functions
- `aa_audit_file` emits file-specific audit records.
- `aa_lookup_condperms` and `aa_str_perms` translate DFA states into conditional `aa_perms`.
- `aa_path_perm` and `__aa_path_perm` mediate named paths.
- `aa_path_link` and `profile_path_link` mediate hardlinks and subset constraints.
- `aa_file_perm` revalidates already-open files using `aa_file_ctx`.
- `aa_inherit_files` revalidates inherited descriptors and replaces unauthorized ones with `aa_null`.

## Control flow
Path checks resolve a path name with profile path flags, build a `path_cond` from inode owner/mode, match the file policy DFA, apply permissions, audit, and return errors. Link checks first match the link name, then transition through a NUL-separated pair to match the target; optional subset checks ensure permissions on the link do not exceed target permissions and exec xindex flags are compatible.

Open-file revalidation first checks cached `file_ctx` label and allowed mask under RCU. If the subject label is already cached and requested permissions are covered, the fast path returns. Otherwise it obtains the newest cached file label and revalidates either path-mediated files or sockets, updating `file_ctx` on success. Inherited descriptors are scanned with `iterate_fd`; unauthorized files are replaced with the apparmorfs `.null` device.

## State and persistence
Each `struct file` carries AppArmor blob state `aa_file_ctx` with a spinlock, cached label, and allowed permission mask. The file also relies on global `aa_null` created by apparmorfs. No disk state is written, but cached permissions persist for the lifetime of open file objects.

## Dependencies and integration
The file depends on path naming, policy DFA matching, audit, labels, network/socket mediation, AF_UNIX revalidation, VFS file modes, and kernel fd/tty APIs. Domain transition code calls `aa_inherit_files` to enforce new labels against existing descriptors.

## Risks
Comments explicitly note no revocation on stale profiles and incomplete cached full-permission tracking, so policy replacement may not revoke already-open access immediately. Hardlink subset logic is security sensitive. Deleted/disconnected path handling depends on path flags. In atomic contexts, buffer allocation failures can deny access.

## Test signals
Test read/write/append/create/truncate/open/getattr/setattr/chmod/chown/lock/mmap_exec path permissions; owner conditional rules; hardlink pair and subset failures; profile replacement with open files; inherited fd replacement with `.null`; controlling TTY drop; and socket file revalidation including Unix peer changes. Audit masks should match requested and denied permissions.
