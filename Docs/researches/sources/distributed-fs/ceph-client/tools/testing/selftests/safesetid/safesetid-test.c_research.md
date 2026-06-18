<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.c

## Purpose

Privilege-heavy SafeSetID LSM functional test. It installs UID/GID allowlist policy, creates test passwd/group entries when absent, drops into restricted identities, and verifies allowed and denied setuid, setgid, setgroups, and user namespace uid_map operations.

## Important APIs, Types, and Functions

Uses securityfs policy files /sys/kernel/security/safesetid/uid_allowlist_policy and gid_allowlist_policy, mount(securityfs), libcap cap_get_proc/cap_set_flag/cap_set_proc, prctl(PR_SET_KEEPCAPS/PR_SET_DUMPABLE), setuid, setgid, setgroups, clone(CLONE_NEWUSER), /proc/<pid>/uid_map writes, waitpid, passwd/group database APIs, and fork.

## Control Flow and Integration

main creates required users/groups, mounts securityfs if needed, writes policy 1->2, 1->3, 2->2, 3->3, then first proves an unrestricted uid with CAP_SETUID can write a user namespace map. It switches to restricted uid/gid 1, checks allowed child IDs 2 and 3 and denied root/no-policy IDs for UID, GID, supplemental groups, and userns mapping, then drops all caps and verifies all setid attempts fail.

## State and Persistence Behavior

Persists changes to /etc/passwd and /etc/group and appends SafeSetID policy through securityfs. It does not clean up accounts or policy. Runtime children communicate outcomes only by exit status.

## Dependencies and Integration Points

Requires libcap development/runtime support, root privileges, CONFIG_SECURITYFS and CONFIG_SAFESETID, writable /etc/passwd and /etc/group, securityfs, and user namespace support for the userns case.

## Risks and Edge Cases

This test mutates host identity databases and LSM policy, so it is best isolated in a test VM/container. Policy persistence and account collisions can affect later tests. User namespace restrictions or distro security settings can alter expected clone/map behavior.

## Test Signals

Pass signal is the final "test successful" after every expected allowed/denied transition matches. Failures abort through die(), making the first unexpected policy behavior visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.c -->
