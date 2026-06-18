# sources/distributed-fs/ceph-client/scripts/selinux/install_policy.sh

Purpose: `install_policy.sh` installs a generated dummy SELinux policy under `/etc/selinux/dummy` and arranges permissive boot-time activation/relabeling.

Important APIs, types, and functions: it requires root, locates `setfiles`, `checkpolicy`, and `selinuxenabled`, obtains policy version via `checkpolicy -V`, runs `mdp -m policy.conf file_contexts`, compiles the policy with `checkpolicy -U allow -M`, creates SELinux directory structure and context files, copies generated policy/context artifacts, writes `/etc/selinux/config`, runs `setfiles`, and creates `/.autorelabel`.

Control flow: after dependency checks, it refuses to proceed if SELinux is currently enabled because relabeling all files is unsafe. It builds the dummy policy in `mdp`, populates `/etc/selinux/dummy`, backs up an existing `/etc/selinux/config`, relabels `/` plus selected mounted filesystem roots, and schedules autorelabel.

State and persistence: it writes system policy files, may rename `/etc/selinux/config` to `.bak`, relabels filesystem labels, and writes `/.autorelabel`. This is intentionally invasive.

Dependencies and integration points: depends on the `mdp` host binary, SELinux userspace tools, root permissions, and Linux filesystem layout. It is a helper for testing/bootstrapping SELinux rather than normal kernel build output.

Risks: the script has broad host-system side effects and should not be run accidentally. The mount-list command uses shell/awk quoting that should be reviewed before changes. Running on an active SELinux system is blocked but permissive/relabel behavior still affects the machine.

Test signals: test only in disposable VMs or containers with appropriate privileges. Validate generated policy compiles, expected files exist, `/etc/selinux/config` content is correct, and relabel commands receive intended mount paths.
