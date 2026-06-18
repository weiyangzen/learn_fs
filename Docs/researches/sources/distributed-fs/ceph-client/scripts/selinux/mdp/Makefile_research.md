# sources/distributed-fs/ceph-client/scripts/selinux/mdp/Makefile

Purpose: this Makefile builds the SELinux `mdp` host program and declares its cleanup outputs.

Important APIs, types, and functions: `hostprogs-always-y += mdp` always builds the host tool. `HOST_EXTRACFLAGS` adds include paths for kernel headers, SELinux headers, and generated object-tree includes. `clean-files := policy.* file_contexts` removes generated policy outputs.

Control flow: Kbuild consumes these variables during host tools build and clean phases.

State and persistence: build state includes the `mdp` executable and generated policy artifacts cleaned by `make clean`.

Dependencies and integration points: depends on `mdp.c` and generated/in-tree headers such as class maps. It is reached through `scripts/selinux/Makefile`.

Risks: incorrect include paths can make `mdp.c` use stale or missing SELinux class/policycap definitions. Cleaning patterns should stay limited to generated outputs.

Test signals: host build should compile `mdp`; `make clean` should remove `policy.*` and `file_contexts` without deleting source files.
