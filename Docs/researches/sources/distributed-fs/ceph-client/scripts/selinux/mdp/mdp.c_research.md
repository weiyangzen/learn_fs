# sources/distributed-fs/ceph-client/scripts/selinux/mdp/mdp.c

Purpose: `mdp.c` generates a minimal dummy SELinux policy and file contexts. The generated policy contains one type with broad self-permissions and enough class, sid, capability, filesystem, role, and user declarations to boot/test SELinux.

Important APIs, types, and functions: it defines `struct security_class_mapping` to satisfy included SELinux class-map data, includes `classmap.h`, `initial_sid_to_string.h`, and `policycap_names.h`, and has a single `main()` with optional `-m` MLS mode. Macros `FS_USE` and `GENFSCON` emit filesystem labeling statements based on kernel config macros.

Control flow: `main()` parses `[-m] policy_file context_file`, writes class declarations, sid declarations, class permissions, optional MLS sensitivities/categories/constraints, all policy capabilities, `base_t`/`base_r` type-role-user statements, allow-all rules for each class, default SID contexts, filesystem labeling rules gated by config, and finally writes two file-context defaults for `/` and `/.*`.

State and persistence: it writes the policy output and context output files supplied on the command line. It has no external state beyond compile-time `CONFIG_*` macros.

Dependencies and integration points: built as a host tool by Kbuild and used by `install_policy.sh`. Its output is consumed by `checkpolicy` and SELinux userspace tools.

Risks: the generated policy grants extremely broad permissions and is only suitable as a dummy/test policy. Filesystem rules are compile-time dependent, so mismatched config headers produce incomplete labels. The OCFS2 string appears as `ocsfs2`, which should be verified against expected filesystem names.

Test signals: compile against current SELinux headers, run with and without `-m`, pass output through `checkpolicy`, and verify generated contexts cover expected configured filesystems.
