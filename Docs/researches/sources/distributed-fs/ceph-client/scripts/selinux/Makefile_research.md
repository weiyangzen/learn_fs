# sources/distributed-fs/ceph-client/scripts/selinux/Makefile

Purpose: this Makefile declares the SELinux script subdirectory build relationship.

Important APIs, types, and functions: it contains `subdir-y := mdp`, telling Kbuild to descend into `scripts/selinux/mdp`.

Control flow: Kbuild interprets the assignment during host-tool build traversal; there is no executable logic in the file.

State and persistence: no runtime state. It affects build graph state by including the `mdp` host program directory.

Dependencies and integration points: integrates with the kernel Kbuild recursive make system and the `mdp/Makefile`.

Risks: removing or changing the subdir entry would stop building the dummy policy generator used by `install_policy.sh`.

Test signals: `make scripts` or a SELinux dummy policy build should descend into `scripts/selinux/mdp` and produce the host `mdp` tool.
